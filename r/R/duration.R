#' Duration parameters for syllable timing
#'
#' Parameters for duration estimation using lognormal models.
#'
#' @param mu Mean of log duration (seconds)
#' @param sigma Standard deviation of log duration
#' @param speaker_effect Multiplicative speaker effect
#' @param fatigue_coeff Linear fatigue effect per syllable
#' @param vowel_duration_mult Vowel duration multiplier
#' @param consonant_duration_mult Consonant duration multiplier
#' @param stressed_mult Stressed syllable multiplier
#' @param unstressed_mult Unstressed syllable multiplier
#' @return List of duration parameters
#' @noRd
.duration_params <- function(
  mu = 0.15,
  sigma = 0.3,
  speaker_effect = 1.0,
  fatigue_coeff = 0.0,
  vowel_duration_mult = 1.0,
  consonant_duration_mult = 1.0,
  stressed_mult = 1.2,
  unstressed_mult = 0.9
) {
  list(
    mu = mu,
    sigma = sigma,
    speaker_effect = speaker_effect,
    fatigue_coeff = fatigue_coeff,
    vowel_duration_mult = vowel_duration_mult,
    consonant_duration_mult = consonant_duration_mult,
    stressed_mult = stressed_mult,
    unstressed_mult = unstressed_mult
  )
}

#' Calculate expected syllable duration using lognormal model
#'
#' Calculate expected syllable duration using lognormal model.
#'
#' @param params Duration parameters (uses defaults if NULL)
#' @return Expected syllable duration in seconds
#' @export
expected_syllable_duration <- function(params = NULL) {
  if (is.null(params)) {
    params <- .duration_params()
  }
  
  # Lognormal mean: exp(mu + sigma^2/2)
  lognormal_mean <- exp(params$mu + (params$sigma^2) / 2)
  
  # Apply speaker effect
  return(lognormal_mean * params$speaker_effect)
}

#' Calculate variance of syllable duration using lognormal model
#'
#' Calculate variance of syllable duration using lognormal model.
#'
#' @param params Duration parameters (uses defaults if NULL)
#' @return Variance of syllable duration in seconds^2
#' @export
variance_syllable_duration <- function(params = NULL) {
  if (is.null(params)) {
    params <- .duration_params()
  }
  
  # Lognormal variance: exp(2*mu + sigma^2) * (exp(sigma^2) - 1)
  variance <- exp(2 * params$mu + params$sigma^2) * (exp(params$sigma^2) - 1)
  
  # Apply speaker effect squared
  return(variance * (params$speaker_effect^2))
}

#' Calculate expected duration for a given number of syllables
#'
#' Calculate expected duration for a given number of syllables.
#'
#' @param num_syllables Number of syllables
#' @param params Duration parameters
#' @return Expected total duration in seconds
#' @export
expected_duration_for_syllables <- function(num_syllables, params = NULL) {
  if (is.null(params)) {
    params <- .duration_params()
  }
  
  base_duration <- expected_syllable_duration(params)
  
  # Apply fatigue effect
  fatigue_effect <- 1.0 + params$fatigue_coeff * num_syllables
  
  return(base_duration * num_syllables * fatigue_effect)
}

#' Calculate variance of duration for a given number of syllables
#'
#' Calculate variance of duration for a given number of syllables.
#'
#' @param num_syllables Number of syllables
#' @param params Duration parameters
#' @return Variance of total duration in seconds^2
#' @export
variance_duration_for_syllables <- function(num_syllables, params = NULL) {
  if (is.null(params)) {
    params <- .duration_params()
  }
  
  base_variance <- variance_syllable_duration(params)
  
  # For independent syllables, variance scales linearly
  return(base_variance * num_syllables)
}

#' Get default duration parameters
#'
#' Get default duration parameters.
#'
#' @return Default duration parameters
#' @export
get_default_params <- function() {
  return(.duration_params())
}

#' Create duration parameters with specified values
#'
#' Create duration parameters with specified values.
#'
#' @param mu Mean of log duration
#' @param sigma Standard deviation of log duration
#' @param speaker_effect Speaker effect multiplier
#' @param fatigue_coeff Fatigue coefficient
#' @param ... Additional parameters
#' @return Duration parameters object
#' @export
create_params <- function(
  mu = NULL,
  sigma = NULL,
  speaker_effect = NULL,
  fatigue_coeff = NULL,
  ...
) {
  params <- get_default_params()
  
  if (!is.null(mu)) params$mu <- mu
  if (!is.null(sigma)) params$sigma <- sigma
  if (!is.null(speaker_effect)) params$speaker_effect <- speaker_effect
  if (!is.null(fatigue_coeff)) params$fatigue_coeff <- fatigue_coeff
  
  # Update any additional parameters
  additional <- list(...)
  for (name in names(additional)) {
    if (name %in% names(params)) {
      params[[name]] <- additional[[name]]
    }
  }
  
  return(params)
}
