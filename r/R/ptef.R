#' Main PTEF module for pronunciation time estimation
#'
#' Orchestrates all components to estimate pronunciation time
#' for numerical sequences in Brazilian Portuguese.
#'
#' @param N Maximum number to estimate for
#' @param policy Grammar policy (currently only "R1" supported)
#' @param B Block size for structural pauses
#' @param params PTEF parameters (uses defaults if NULL)
#' @param return_ci Whether to return confidence intervals
#' @return List containing mean, var, ci95 (if return_ci=TRUE), and details
#' @export
estimate <- function(
  N,
  policy = "R1",
  B = 16,
  params = NULL,
  return_ci = TRUE
) {
  if (is.null(params)) {
    params <- .ptef_params()
  }
  
  # Get token counts
  result <- count_tokens_up_to_n(N, policy)
  token_counts <- result$tokens
  connective_counts <- result$connectives
  
  # Count syllables
  total_syllables <- count_syllables_up_to_n(N, policy)
  
  # Calculate syllable duration
  syllable_duration <- expected_duration_for_syllables(
    total_syllables, 
    params$duration_params
  )
  syllable_variance <- variance_duration_for_syllables(
    total_syllables, 
    params$duration_params
  )
  
  # Calculate pause duration
  pause_counts <- count_pauses(
    token_counts, 
    B, 
    params$include_structural_pauses,
    params$pause_params
  )
  
  pause_duration <- expected_pause_duration(pause_counts, params$pause_params)
  pause_variance <- variance_pause_duration(pause_counts, params$pause_params)
  
  # Total duration and variance
  total_duration <- syllable_duration + pause_duration
  total_variance <- syllable_variance + pause_variance
  
  # Calculate confidence interval
  ci95 <- NULL
  if (return_ci) {
    std_dev <- sqrt(total_variance)
    ci95 <- list(
      lower = total_duration - 1.96 * std_dev,
      upper = total_duration + 1.96 * std_dev
    )
  }
  
  # Prepare details
  details <- list(
    total_syllables = total_syllables,
    syllable_duration = syllable_duration,
    syllable_variance = syllable_variance,
    pause_counts = pause_counts,
    pause_duration = pause_duration,
    pause_variance = pause_variance,
    token_counts = token_counts,
    connective_counts = connective_counts
  )
  
  result <- list(
    mean = total_duration,
    var = total_variance,
    details = details
  )
  
  if (!is.null(ci95)) {
    result$ci95 <- ci95
  }
  
  return(result)
}

#' PTEF parameters for estimation
#'
#' Parameters for PTEF estimation including duration and pause parameters.
#'
#' @param duration_params Duration parameters
#' @param pause_params Pause parameters
#' @param block_size Block size for structural pauses
#' @param include_structural_pauses Whether to include structural pauses
#' @return List of PTEF parameters
#' @noRd
.ptef_params <- function(
  duration_params = NULL,
  pause_params = NULL,
  block_size = 16,
  include_structural_pauses = TRUE
) {
  if (is.null(duration_params)) {
    duration_params <- get_default_params()
  }
  if (is.null(pause_params)) {
    pause_params <- get_default_pause_params()
  }
  
  list(
    duration_params = duration_params,
    pause_params = pause_params,
    block_size = block_size,
    include_structural_pauses = include_structural_pauses
  )
}

#' Get default PTEF parameters
#'
#' Get default PTEF parameters.
#'
#' @return Default PTEF parameters
#' @export
get_default_params <- function() {
  return(.ptef_params())
}

#' Create PTEF parameters with specified values
#'
#' Create PTEF parameters with specified values.
#'
#' @param duration_params Duration parameters
#' @param pause_params Pause parameters
#' @param block_size Block size for structural pauses
#' @param include_structural_pauses Whether to include structural pauses
#' @param ... Additional parameters
#' @return PTEF parameters object
#' @export
create_params <- function(
  duration_params = NULL,
  pause_params = NULL,
  block_size = NULL,
  include_structural_pauses = NULL,
  ...
) {
  params <- get_default_params()
  
  if (!is.null(duration_params)) params$duration_params <- duration_params
  if (!is.null(pause_params)) params$pause_params <- pause_params
  if (!is.null(block_size)) params$block_size <- block_size
  if (!is.null(include_structural_pauses)) params$include_structural_pauses <- include_structural_pauses
  
  # Update any additional parameters
  additional <- list(...)
  for (name in names(additional)) {
    if (name %in% names(params)) {
      params[[name]] <- additional[[name]]
    }
  }
  
  return(params)
}

#' Estimate pronunciation time for multiple N values
#'
#' Estimate pronunciation time for multiple N values.
#'
#' @param N_values Vector of N values to estimate for
#' @param policy Grammar policy
#' @param B Block size for structural pauses
#' @param params PTEF parameters
#' @return List mapping N values to estimation results
#' @export
estimate_batch <- function(
  N_values,
  policy = "R1",
  B = 16,
  params = NULL
) {
  results <- list()
  
  for (N in N_values) {
    results[[as.character(N)]] <- estimate(N, policy, B, params, return_ci = TRUE)
  }
  
  return(results)
}
