# Tests for lexicon module

test_that("syllables counts basic syllables correctly", {
  expect_equal(syllables("um"), 1)
  expect_equal(syllables("dois"), 1)
  expect_equal(syllables("três"), 1)
  expect_equal(syllables("quatro"), 2)
  expect_equal(syllables("cinco"), 2)
})

test_that("syllables counts connectives correctly", {
  expect_equal(syllables("e"), 1)
})

test_that("syllables counts hundreds correctly", {
  expect_equal(syllables("cem"), 1)
  expect_equal(syllables("cento"), 2)
  expect_equal(syllables("duzentos"), 3)
  expect_equal(syllables("quatrocentos"), 4)
})

test_that("syllables counts thousands correctly", {
  expect_equal(syllables("mil"), 1)
  expect_equal(syllables("milhão"), 2)
  expect_equal(syllables("milhões"), 2)
})

test_that("syllables handles unknown tokens", {
  expect_error(syllables("unknown_token"), "Token 'unknown_token' not found in lexicon")
})

test_that("get_available_tokens returns available tokens", {
  tokens <- get_available_tokens()
  
  # Check that basic tokens are available
  expect_true("um" %in% tokens)
  expect_true("dois" %in% tokens)
  expect_true("e" %in% tokens)
  expect_true("mil" %in% tokens)
  
  # Check that it returns a character vector
  expect_type(tokens, "character")
})

test_that("validate_tokens validates correctly", {
  # Test with valid tokens
  valid_tokens <- c("um", "dois", "e", "mil")
  validation <- validate_tokens(valid_tokens)
  
  for (token in valid_tokens) {
    expect_true(validation[token])
  }
  
  # Test with invalid tokens
  invalid_tokens <- c("um", "unknown_token", "e")
  validation <- validate_tokens(invalid_tokens)
  
  expect_true(validation["um"])
  expect_true(validation["e"])
  expect_false(validation["unknown_token"])
})

test_that("lexicon is consistent", {
  # Test that the same token always returns the same syllable count
  for (token in c("um", "dois", "três", "quatro", "cinco")) {
    count1 <- syllables(token)
    count2 <- syllables(token)
    expect_equal(count1, count2)
  }
})

test_that("lexicon covers all generated tokens", {
  # Generate tokens for numbers 1-100
  all_tokens <- character(0)
  for (n in 1:100) {
    tokens <- text_number(n)
    all_tokens <- c(all_tokens, tokens)
  }
  all_tokens <- unique(all_tokens)
  
  # Validate that all tokens are in lexicon
  validation <- validate_tokens(all_tokens)
  
  # All tokens should be valid
  for (token in names(validation)) {
    expect_true(validation[token], info = paste("Token '", token, "' not found in lexicon", sep = ""))
  }
})
