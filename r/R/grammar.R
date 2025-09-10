#' Generate Portuguese number words
#'
#' Generate Portuguese number words for numbers 1 to n using the R1 policy
#' with proper "e" (and) connective rules.
#'
#' @param n Maximum number to generate words for
#' @param policy Grammar policy (currently only "R1" supported)
#' @return Character vector of tokens representing the number in Portuguese
#' @export
text_number <- function(n, policy = "R1") {
  if (n < 0) {
    stop("n must be non-negative")
  }
  if (policy != "R1") {
    stop("Only R1 policy is currently supported")
  }
  
  if (n == 0) {
    return("zero")
  }
  
  return(.generate_tokens(n))
}

#' Generate tokens for a given number
#' @param n Number to generate tokens for
#' @return Character vector of tokens
#' @noRd
.generate_tokens <- function(n) {
  if (n == 0) {
    return(character(0))
  }
  
  # Handle special cases for 1-19
  if (n >= 1 && n <= 19) {
    return(.units_tokens(n))
  }
  
  # Handle 20-99
  if (n >= 20 && n <= 99) {
    return(.tens_tokens(n))
  }
  
  # Handle 100-199
  if (n >= 100 && n <= 199) {
    return(.hundreds_tokens(n))
  }
  
  # Handle 200-999
  if (n >= 200 && n <= 999) {
    return(.hundreds_tokens(n))
  }
  
  # Handle 1000-999999
  if (n >= 1000 && n <= 999999) {
    return(.thousands_tokens(n))
  }
  
  # Handle millions
  if (n >= 1000000 && n <= 999999999) {
    return(.millions_tokens(n))
  }
  
  # Handle billions
  if (n >= 1000000000 && n <= 999999999999) {
    return(.billions_tokens(n))
  }
  
  stop(paste("Number", n, "is too large for current implementation"))
}

#' Generate tokens for units (1-19)
#' @param n Number in range 1-19
#' @return Character vector of tokens
#' @noRd
.units_tokens <- function(n) {
  units <- c("", "um", "dois", "três", "quatro", "cinco", "seis", "sete", 
             "oito", "nove", "dez", "onze", "doze", "treze", "quatorze", 
             "quinze", "dezesseis", "dezessete", "dezoito", "dezenove")
  
  if (n >= 1 && n <= 19) {
    return(units[n + 1])  # R is 1-indexed
  }
  return(character(0))
}

#' Generate tokens for tens (20-99)
#' @param n Number in range 20-99
#' @return Character vector of tokens
#' @noRd
.tens_tokens <- function(n) {
  tens <- c("", "", "vinte", "trinta", "quarenta", "cinquenta", 
            "sessenta", "setenta", "oitenta", "noventa")
  
  tens_digit <- n %/% 10
  units_digit <- n %% 10
  
  tokens <- tens[tens_digit + 1]  # R is 1-indexed
  
  if (units_digit > 0) {
    tokens <- c(tokens, "e", .units_tokens(units_digit))
  }
  
  return(tokens)
}

#' Generate tokens for hundreds (100-999)
#' @param n Number in range 100-999
#' @return Character vector of tokens
#' @noRd
.hundreds_tokens <- function(n) {
  hundreds_digit <- n %/% 100
  remainder <- n %% 100
  
  if (n == 100) {
    return("cem")
  }
  
  if (hundreds_digit == 1) {
    tokens <- "cento"
  } else {
    hundreds_words <- c("", "", "duzentos", "trezentos", "quatrocentos", 
                       "quinhentos", "seiscentos", "setecentos", 
                       "oitocentos", "novecentos")
    tokens <- hundreds_words[hundreds_digit + 1]  # R is 1-indexed
  }
  
  if (remainder > 0) {
    if (remainder < 20) {
      tokens <- c(tokens, "e", .units_tokens(remainder))
    } else {
      tens_tokens <- .tens_tokens(remainder)
      if (length(tens_tokens) > 0) {
        tokens <- c(tokens, "e", tens_tokens)
      }
    }
  }
  
  return(tokens)
}

#' Generate tokens for thousands (1000-999999)
#' @param n Number in range 1000-999999
#' @return Character vector of tokens
#' @noRd
.thousands_tokens <- function(n) {
  thousands <- n %/% 1000
  remainder <- n %% 1000
  
  if (thousands == 1) {
    tokens <- "mil"
  } else {
    thousands_tokens <- .generate_tokens(thousands)
    tokens <- c(thousands_tokens, "mil")
  }
  
  if (remainder > 0) {
    if (remainder < 100) {
      tokens <- c(tokens, "e", .generate_tokens(remainder))
    } else {
      remainder_tokens <- .generate_tokens(remainder)
      if (length(remainder_tokens) > 0) {
        tokens <- c(tokens, "e", remainder_tokens)
      }
    }
  }
  
  return(tokens)
}

#' Generate tokens for millions (1000000-999999999)
#' @param n Number in range 1000000-999999999
#' @return Character vector of tokens
#' @noRd
.millions_tokens <- function(n) {
  millions <- n %/% 1000000
  remainder <- n %% 1000000
  
  if (millions == 1) {
    tokens <- c("um", "milhão")
  } else {
    millions_tokens <- .generate_tokens(millions)
    tokens <- c(millions_tokens, "milhões")
  }
  
  if (remainder > 0) {
    if (remainder < 100) {
      tokens <- c(tokens, "e", .generate_tokens(remainder))
    } else {
      remainder_tokens <- .generate_tokens(remainder)
      if (length(remainder_tokens) > 0) {
        tokens <- c(tokens, "e", remainder_tokens)
      }
    }
  }
  
  return(tokens)
}

#' Generate tokens for billions (1000000000-999999999999)
#' @param n Number in range 1000000000-999999999999
#' @return Character vector of tokens
#' @noRd
.billions_tokens <- function(n) {
  billions <- n %/% 1000000000
  remainder <- n %% 1000000000
  
  if (billions == 1) {
    tokens <- c("um", "bilhão")
  } else {
    billions_tokens <- .generate_tokens(billions)
    tokens <- c(billions_tokens, "bilhões")
  }
  
  if (remainder > 0) {
    if (remainder < 100) {
      tokens <- c(tokens, "e", .generate_tokens(remainder))
    } else {
      remainder_tokens <- .generate_tokens(remainder)
      if (length(remainder_tokens) > 0) {
        tokens <- c(tokens, "e", remainder_tokens)
      }
    }
  }
  
  return(tokens)
}
