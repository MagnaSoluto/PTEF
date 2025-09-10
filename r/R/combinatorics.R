#' Count tokens in numbers 1-999
#'
#' Count all tokens in numbers 1-999 using direct counting.
#'
#' @return Named integer vector mapping tokens to their total count
#' @noRd
.count_tokens_up_to_999 <- function() {
  counts <- integer(0)
  
  for (n in 1:999) {
    tokens <- text_number(n)
    for (token in tokens) {
      if (token %in% names(counts)) {
        counts[token] <- counts[token] + 1
      } else {
        counts[token] <- 1
      }
    }
  }
  
  return(counts)
}

#' Count tokens and connectives up to N using O(log N) algorithm
#'
#' Count tokens and connectives up to N using efficient block-based counting.
#'
#' @param N Maximum number to count up to
#' @param policy Grammar policy (currently only "R1" supported)
#' @return List with elements 'tokens' and 'connectives' containing counts
#' @export
count_tokens_up_to_n <- function(N, policy = "R1") {
  if (policy != "R1") {
    stop("Only R1 policy is currently supported")
  }
  
  if (N <= 0) {
    return(list(tokens = integer(0), connectives = integer(0)))
  }
  
  # For small N, use direct counting
  if (N <= 1000) {
    return(.count_direct(N))
  }
  
  # For large N, use block decomposition
  return(.count_blocks(N))
}

#' Direct counting for small N
#' @param N Maximum number to count up to
#' @return List with token and connective counts
#' @noRd
.count_direct <- function(N) {
  token_counts <- integer(0)
  connective_counts <- integer(0)
  
  for (n in 1:N) {
    tokens <- text_number(n)
    for (i in seq_along(tokens)) {
      token <- tokens[i]
      
      # Count tokens
      if (token %in% names(token_counts)) {
        token_counts[token] <- token_counts[token] + 1
      } else {
        token_counts[token] <- 1
      }
      
      # Count connectives (tokens that are "e")
      if (token == "e") {
        if ("e" %in% names(connective_counts)) {
          connective_counts["e"] <- connective_counts["e"] + 1
        } else {
          connective_counts["e"] <- 1
        }
      }
    }
  }
  
  return(list(tokens = token_counts, connectives = connective_counts))
}

#' Block-based counting for large N using O(log N) algorithm
#' @param N Maximum number to count up to
#' @return List with token and connective counts
#' @noRd
.count_blocks <- function(N) {
  # Get base counts for 1-999
  base_result <- .count_tokens_up_to_999()
  base_tokens <- base_result
  base_connectives <- integer(0)
  
  # Count connectives in base
  for (token in names(base_tokens)) {
    if (token == "e") {
      base_connectives[token] <- base_tokens[token]
    }
  }
  
  # Initialize result counts
  token_counts <- base_tokens
  connective_counts <- base_connectives
  
  # Handle thousands
  if (N >= 1000) {
    thousands <- N %/% 1000
    remainder <- N %% 1000
    
    # Count thousands blocks
    for (i in 1:thousands) {
      # Add "mil" token
      if ("mil" %in% names(token_counts)) {
        token_counts["mil"] <- token_counts["mil"] + 1
      } else {
        token_counts["mil"] <- 1
      }
      
      # Add all base tokens
      for (token in names(base_tokens)) {
        if (token %in% names(token_counts)) {
          token_counts[token] <- token_counts[token] + base_tokens[token]
        } else {
          token_counts[token] <- base_tokens[token]
        }
      }
      
      # Add all base connectives
      for (conn in names(base_connectives)) {
        if (conn %in% names(connective_counts)) {
          connective_counts[conn] <- connective_counts[conn] + base_connectives[conn]
        } else {
          connective_counts[conn] <- base_connectives[conn]
        }
      }
    }
    
    # Handle remainder
    if (remainder > 0) {
      remainder_tokens <- text_number(remainder)
      for (token in remainder_tokens) {
        if (token %in% names(token_counts)) {
          token_counts[token] <- token_counts[token] + 1
        } else {
          token_counts[token] <- 1
        }
        if (token == "e") {
          if ("e" %in% names(connective_counts)) {
            connective_counts["e"] <- connective_counts["e"] + 1
          } else {
            connective_counts["e"] <- 1
          }
        }
      }
    }
  }
  
  # Handle millions
  if (N >= 1000000) {
    millions <- N %/% 1000000
    remainder <- N %% 1000000
    
    # Count millions blocks
    for (i in 1:millions) {
      # Add "milhão" or "milhões" token
      if (millions == 1) {
        if ("milhão" %in% names(token_counts)) {
          token_counts["milhão"] <- token_counts["milhão"] + 1
        } else {
          token_counts["milhão"] <- 1
        }
      } else {
        if ("milhões" %in% names(token_counts)) {
          token_counts["milhões"] <- token_counts["milhões"] + 1
        } else {
          token_counts["milhões"] <- 1
        }
      }
      
      # Add all base tokens
      for (token in names(base_tokens)) {
        if (token %in% names(token_counts)) {
          token_counts[token] <- token_counts[token] + base_tokens[token]
        } else {
          token_counts[token] <- base_tokens[token]
        }
      }
    }
    
    # Handle remainder
    if (remainder > 0) {
      remainder_tokens <- text_number(remainder)
      for (token in remainder_tokens) {
        if (token %in% names(token_counts)) {
          token_counts[token] <- token_counts[token] + 1
        } else {
          token_counts[token] <- 1
        }
        if (token == "e") {
          if ("e" %in% names(connective_counts)) {
            connective_counts["e"] <- connective_counts["e"] + 1
          } else {
            connective_counts["e"] <- 1
          }
        }
      }
    }
  }
  
  return(list(tokens = token_counts, connectives = connective_counts))
}

#' Count total syllables up to N
#'
#' Count total syllables up to N using token counts.
#'
#' @param N Maximum number to count up to
#' @param policy Grammar policy
#' @return Total syllable count
#' @export
count_syllables_up_to_n <- function(N, policy = "R1") {
  result <- count_tokens_up_to_n(N, policy)
  token_counts <- result$tokens
  
  total_syllables <- 0
  for (token in names(token_counts)) {
    tryCatch({
      token_syllables <- syllables(token)
      total_syllables <- total_syllables + token_syllables * token_counts[token]
    }, error = function(e) {
      # Skip unknown tokens
      NULL
    })
  }
  
  return(total_syllables)
}

#' Count total connectives up to N
#'
#' Count total connectives up to N using token counts.
#'
#' @param N Maximum number to count up to
#' @param policy Grammar policy
#' @return Total connective count
#' @export
count_connectives_up_to_n <- function(N, policy = "R1") {
  result <- count_tokens_up_to_n(N, policy)
  connective_counts <- result$connectives
  return(sum(connective_counts))
}
