# Tests for duration module

test_that("expected_syllable_duration calculates correctly", {
  params <- get_default_params()
  duration <- expected_syllable_duration(params)
  
  # Should be positive
  expect_true(duration > 0)
  
  # Should be approximately exp(mu + sigma^2/2) * speaker_effect
  expected <- exp(params$mu + (params$sigma^2) / 2) * params$speaker_effect
  expect_equal(duration, expected, tolerance = 1e-10)
})

test_that("variance_syllable_duration calculates correctly", {
  params <- get_default_params()
  variance <- variance_syllable_duration(params)
  
  # Should be positive
  expect_true(variance > 0)
  
  # Should be approximately exp(2*mu + sigma^2) * (exp(sigma^2) - 1) * speaker_effect^2
  expected <- exp(2 * params$mu + params$sigma^2) * (exp(params$sigma^2) - 1) * (params$speaker_effect^2)
  expect_equal(variance, expected, tolerance = 1e-10)
})

test_that("expected_duration_for_syllables works", {
  params <- get_default_params()
  
  # Test with 1 syllable
  duration_1 <- expected_duration_for_syllables(1, params)
  expect_true(duration_1 > 0)
  
  # Test with 10 syllables
  duration_10 <- expected_duration_for_syllables(10, params)
  expect_true(duration_10 > duration_1)
  expect_equal(duration_10, 10 * duration_1)  # Should scale linearly without fatigue
})

test_that("variance_duration_for_syllables works", {
  params <- get_default_params()
  
  # Test with 1 syllable
  variance_1 <- variance_duration_for_syllables(1, params)
  expect_true(variance_1 > 0)
  
  # Test with 10 syllables
  variance_10 <- variance_duration_for_syllables(10, params)
  expect_true(variance_10 > variance_1)
  expect_equal(variance_10, 10 * variance_1)  # Should scale linearly
})

test_that("fatigue effect works", {
  params_no_fatigue <- create_params(fatigue_coeff = 0.0)
  params_with_fatigue <- create_params(fatigue_coeff = 0.01)
  
  duration_no_fatigue <- expected_duration_for_syllables(100, params_no_fatigue)
  duration_with_fatigue <- expected_duration_for_syllables(100, params_with_fatigue)
  
  # With fatigue, duration should be longer
  expect_true(duration_with_fatigue > duration_no_fatigue)
})

test_that("speaker effect works", {
  params_normal <- create_params(speaker_effect = 1.0)
  params_slow <- create_params(speaker_effect = 1.5)
  
  duration_normal <- expected_syllable_duration(params_normal)
  duration_slow <- expected_syllable_duration(params_slow)
  
  # Slow speaker should have longer duration
  expect_true(duration_slow > duration_normal)
  expect_equal(duration_slow, 1.5 * duration_normal)
})

test_that("get_default_params works", {
  params <- get_default_params()
  expect_type(params, "list")
  expect_equal(params$mu, 0.15)
  expect_equal(params$sigma, 0.3)
})

test_that("create_params works", {
  params <- create_params(
    mu = 0.2,
    sigma = 0.4,
    speaker_effect = 1.2,
    fatigue_coeff = 0.01
  )
  
  expect_equal(params$mu, 0.2)
  expect_equal(params$sigma, 0.4)
  expect_equal(params$speaker_effect, 1.2)
  expect_equal(params$fatigue_coeff, 0.01)
})

test_that("create_params works with partial values", {
  params <- create_params(mu = 0.2)
  
  expect_equal(params$mu, 0.2)
  expect_equal(params$sigma, 0.3)  # Default value
  expect_equal(params$speaker_effect, 1.0)  # Default value
})

test_that("duration calculations are consistent", {
  params <- get_default_params()
  
  # Test that the same parameters always give the same results
  duration1 <- expected_syllable_duration(params)
  duration2 <- expected_syllable_duration(params)
  expect_equal(duration1, duration2)
  
  variance1 <- variance_syllable_duration(params)
  variance2 <- variance_syllable_duration(params)
  expect_equal(variance1, variance2)
})

test_that("duration scales properly with number of syllables", {
  params <- get_default_params()
  
  # Test scaling from 1 to 10 syllables
  duration_1 <- expected_duration_for_syllables(1, params)
  duration_10 <- expected_duration_for_syllables(10, params)
  
  # Should scale linearly without fatigue
  expect_equal(duration_10, 10 * duration_1, tolerance = 1e-10)
})
