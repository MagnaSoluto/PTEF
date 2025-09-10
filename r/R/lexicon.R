#' Load Brazilian Portuguese number lexicon
#'
#' Load the Brazilian Portuguese number lexicon and provide syllable counting
#' functionality.
#'
#' @return Named integer vector mapping tokens to syllable counts
#' @noRd
.load_lexicon <- function() {
  # Try to load from inst/extdata
  lexicon_path <- system.file("extdata", "bp_number_tokens_syllables.csv", 
                             package = "ptef")
  
  if (file.exists(lexicon_path)) {
    df <- readr::read_csv(lexicon_path, show_col_types = FALSE)
    return(setNames(df$syllables, df$token))
  }
  
  # Fallback to built-in lexicon
  return(c(
    "um" = 1, "dois" = 1, "três" = 1, "quatro" = 2, "cinco" = 2,
    "seis" = 1, "sete" = 2, "oito" = 2, "nove" = 2, "dez" = 1,
    "onze" = 2, "doze" = 2, "treze" = 2, "quatorze" = 3, "quinze" = 2,
    "dezesseis" = 4, "dezessete" = 4, "dezoito" = 3, "dezenove" = 4,
    "vinte" = 2, "trinta" = 2, "quarenta" = 3, "cinquenta" = 3,
    "sessenta" = 3, "setenta" = 3, "oitenta" = 3, "noventa" = 3,
    "cem" = 1, "cento" = 2, "duzentos" = 3, "trezentos" = 3,
    "quatrocentos" = 4, "quinhentos" = 3, "seiscentos" = 3,
    "setecentos" = 4, "oitocentos" = 4, "novecentos" = 4,
    "mil" = 1, "milhão" = 2, "milhões" = 2, "e" = 1
  ))
}

# Global lexicon cache
.lexicon_cache <- NULL

#' Get syllable count for a token
#'
#' Get the syllable count for a given token from the lexicon.
#'
#' @param token The token to count syllables for
#' @return Number of syllables in the token
#' @export
syllables <- function(token) {
  if (is.null(.lexicon_cache)) {
    .lexicon_cache <<- .load_lexicon()
  }
  
  if (!token %in% names(.lexicon_cache)) {
    stop(paste("Token '", token, "' not found in lexicon", sep = ""))
  }
  
  return(.lexicon_cache[token])
}

#' Get available tokens in the lexicon
#'
#' Get the set of all available tokens in the lexicon.
#'
#' @return Character vector of all tokens in the lexicon
#' @export
get_available_tokens <- function() {
  if (is.null(.lexicon_cache)) {
    .lexicon_cache <<- .load_lexicon()
  }
  
  return(names(.lexicon_cache))
}

#' Validate tokens against lexicon
#'
#' Validate that all tokens exist in the lexicon.
#'
#' @param tokens Character vector of tokens to validate
#' @return Named logical vector indicating validation status
#' @export
validate_tokens <- function(tokens) {
  if (is.null(.lexicon_cache)) {
    .lexicon_cache <<- .load_lexicon()
  }
  
  available <- names(.lexicon_cache)
  return(setNames(tokens %in% available, tokens))
}
