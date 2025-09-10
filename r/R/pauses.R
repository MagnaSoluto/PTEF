#' Pause parameters for prosodic pause estimation
#'
#' Parameters for pause estimation based on structural and prosodic boundaries.
#'
#' @param weak_pause_duration Duration of weak pauses (seconds)
#' @param strong_pause_duration Duration of strong pauses (seconds)
#' @param weak_pause_prob Probability of weak pause
#' @param strong_pause_prob Probability of strong pause
#' @param structural_pause_duration Duration of structural pauses (seconds)
#' @param structural_pause_prob Probability of structural pause
#' @return List of pause parameters
#' @noRd
.pause_params <- function(
  weak_pause_duration = 0.1,
  strong_pause_duration = 0.3,
  weak_pause_prob = 0.3,
  strong_pause_prob = 0.1,
  structural_pause_duration = 0.2,
  structural_pause_prob = 0.5
) {
  list(
    weak_pause_duration = weak_pause_duration,
    strong_pause_duration = strong_pause_duration,
    weak_pause_prob = weak_pause_prob,
    strong_pause_prob = strong_pause_prob,
    structural_pause_duration = structural_pause_duration,
    structural_pause_prob = structural_pause_prob
  )
}

#' Count pauses based on token counts and block size
#'
#' Count pauses based on token counts and block size.
#'
#' @param token_counts Named integer vector of token counts
#' @param B Block size for structural pauses
#' @param structural Whether to include structural pauses
#' @param params Pause parameters
#' @return Named integer vector mapping pause types to counts
#' @export
count_pauses <- function(
  token_counts,
  B = 16,
  structural = TRUE,
  params = NULL
) {
  if (is.null(params)) {
    params <- .pause_params()
  }
  
  pause_counts <- c(
    weak_pauses = 0,
    strong_pauses = 0,
    structural_pauses = 0
  )
  
  # Count weak pauses (after connectives)
  if ("e" %in% names(token_counts)) {
    pause_counts["weak_pauses"] <- as.integer(token_counts["e"] * params$weak_pause_prob)
  }
  
  # Count strong pauses (after major boundaries)
  # Strong boundaries occur after "mil", "milhão", "milhões"
  strong_boundary_tokens <- c("mil", "milhão", "milhões")
  for (token in strong_boundary_tokens) {
    if (token %in% names(token_counts)) {
      pause_counts["strong_pauses"] <- pause_counts["strong_pauses"] + 
        as.integer(token_counts[token] * params$strong_pause_prob)
    }
  }
  
  # Count structural pauses (based on block size B)
  if (structural) {
    total_tokens <- sum(token_counts)
    num_blocks <- ceiling(total_tokens / B)
    pause_counts["structural_pauses"] <- as.integer((num_blocks - 1) * params$structural_pause_prob)
  }
  
  return(pause_counts)
}

#' Calculate expected total pause duration
#'
#' Calculate expected total pause duration.
#'
#' @param pause_counts Named integer vector of pause counts
#' @param params Pause parameters
#' @return Expected total pause duration in seconds
#' @export
expected_pause_duration <- function(pause_counts, params = NULL) {
  if (is.null(params)) {
    params <- .pause_params()
  }
  
  total_duration <- 0.0
  
  # Add weak pause duration
  if ("weak_pauses" %in% names(pause_counts)) {
    total_duration <- total_duration + pause_counts["weak_pauses"] * params$weak_pause_duration
  }
  
  # Add strong pause duration
  if ("strong_pauses" %in% names(pause_counts)) {
    total_duration <- total_duration + pause_counts["strong_pauses"] * params$strong_pause_duration
  }
  
  # Add structural pause duration
  if ("structural_pauses" %in% names(pause_counts)) {
    total_duration <- total_duration + pause_counts["structural_pauses"] * params$structural_pause_duration
  }
  
  return(total_duration)
}

#' Calculate variance of total pause duration
#'
#' Calculate variance of total pause duration.
#'
#' @param pause_counts Named integer vector of pause counts
#' @param params Pause parameters
#' @return Variance of total pause duration in seconds^2
#' @export
variance_pause_duration <- function(pause_counts, params = NULL) {
  if (is.null(params)) {
    params <- .pause_params()
  }
  
  # Assume pause durations are independent and normally distributed
  # with variance equal to mean (exponential-like distribution)
  variance <- 0.0
  
  # Add weak pause variance
  if ("weak_pauses" %in% names(pause_counts) && pause_counts["weak_pauses"] > 0) {
    variance <- variance + pause_counts["weak_pauses"] * (params$weak_pause_duration^2)
  }
  
  # Add strong pause variance
  if ("strong_pauses" %in% names(pause_counts) && pause_counts["strong_pauses"] > 0) {
    variance <- variance + pause_counts["strong_pauses"] * (params$strong_pause_duration^2)
  }
  
  # Add structural pause variance
  if ("structural_pauses" %in% names(pause_counts) && pause_counts["structural_pauses"] > 0) {
    variance <- variance + pause_counts["structural_pauses"] * (params$structural_pause_duration^2)
  }
  
  return(variance)
}

#' Get default pause parameters
#'
#' Get default pause parameters.
#'
#' @return Default pause parameters
#' @export
get_default_pause_params <- function() {
  return(.pause_params())
}

#' Create pause parameters with specified values
#'
#' Create pause parameters with specified values.
#'
#' @param weak_pause_duration Duration of weak pauses
#' @param strong_pause_duration Duration of strong pauses
#' @param weak_pause_prob Probability of weak pauses
#' @param strong_pause_prob Probability of strong pauses
#' @param structural_pause_duration Duration of structural pauses
#' @param structural_pause_prob Probability of structural pauses
#' @param ... Additional parameters
#' @return Pause parameters object
#' @export
create_pause_params <- function(
  weak_pause_duration = NULL,
  strong_pause_duration = NULL,
  weak_pause_prob = NULL,
  strong_pause_prob = NULL,
  structural_pause_duration = NULL,
  structural_pause_prob = NULL,
  ...
) {
  params <- get_default_pause_params()
  
  if (!is.null(weak_pause_duration)) params$weak_pause_duration <- weak_pause_duration
  if (!is.null(strong_pause_duration)) params$strong_pause_duration <- strong_pause_duration
  if (!is.null(weak_pause_prob)) params$weak_pause_prob <- weak_pause_prob
  if (!is.null(strong_pause_prob)) params$strong_pause_prob <- strong_pause_prob
  if (!is.null(structural_pause_duration)) params$structural_pause_duration <- structural_pause_duration
  if (!is.null(structural_pause_prob)) params$structural_pause_prob <- structural_pause_prob
  
  # Update any additional parameters
  additional <- list(...)
  for (name in names(additional)) {
    if (name %in% names(params)) {
      params[[name]] <- additional[[name]]
    }
  }
  
  return(params)
}
