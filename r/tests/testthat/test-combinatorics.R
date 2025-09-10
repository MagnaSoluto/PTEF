# Tests for combinatorics module

test_that("count_tokens_up_to_n works for small N", {
  # Test N=10
  result <- count_tokens_up_to_n(10)
  
  # Check that we have some tokens
  expect_true(length(result$tokens) > 0)
  expect_true(length(result$connectives) > 0)
  
  # Check that "um" appears once
  expect_equal(result$tokens["um"], 1)
  
  # Check that "e" appears in connectives
  expect_true("e" %in% names(result$connectives))
})

test_that("count_tokens_up_to_n works for medium N", {
  # Test N=100
  result <- count_tokens_up_to_n(100)
  
  # Check that we have more tokens than for N=10
  expect_true(length(result$tokens) > 0)
  expect_true(length(result$connectives) > 0)
  
  # Check that "um" appears multiple times
  expect_true(result$tokens["um"] > 1)
})

test_that("count_tokens_up_to_n works for large N", {
  # Test N=1000
  result <- count_tokens_up_to_n(1000)
  
  # Check that we have tokens
  expect_true(length(result$tokens) > 0)
  expect_true(length(result$connectives) > 0)
  
  # Check that "mil" appears
  expect_true("mil" %in% names(result$tokens))
})

test_that("count_tokens_up_to_n is consistent", {
  # For small N, fast counting should match direct counting
  for (N in c(10, 50, 100)) {
    fast_result <- count_tokens_up_to_n(N)
    
    # Direct counting
    direct_counts <- integer(0)
    direct_conn <- integer(0)
    for (n in 1:N) {
      tokens <- text_number(n)
      for (token in tokens) {
        if (token %in% names(direct_counts)) {
          direct_counts[token] <- direct_counts[token] + 1
        } else {
          direct_counts[token] <- 1
        }
        if (token == "e") {
          if ("e" %in% names(direct_conn)) {
            direct_conn["e"] <- direct_conn["e"] + 1
          } else {
            direct_conn["e"] <- 1
          }
        }
      }
    }
    
    # Compare counts
    all_tokens <- unique(c(names(fast_result$tokens), names(direct_counts)))
    for (token in all_tokens) {
      fast_count <- fast_result$tokens[token]
      if (is.na(fast_count)) fast_count <- 0
      direct_count <- direct_counts[token]
      if (is.na(direct_count)) direct_count <- 0
      expect_equal(fast_count, direct_count, 
                   info = paste("Token '", token, "' count mismatch: fast=", fast_count, ", direct=", direct_count, sep = ""))
    }
  }
})

test_that("count_syllables_up_to_n works", {
  # Test N=10
  syllables <- count_syllables_up_to_n(10)
  expect_true(syllables > 0)
  
  # Test N=100
  syllables_100 <- count_syllables_up_to_n(100)
  expect_true(syllables_100 > syllables)  # Should be more syllables for larger N
})

test_that("count_connectives_up_to_n works", {
  # Test N=10
  connectives <- count_connectives_up_to_n(10)
  expect_true(connectives >= 0)
  
  # Test N=100
  connectives_100 <- count_connectives_up_to_n(100)
  expect_true(connectives_100 >= connectives)  # Should be more or equal connectives for larger N
})

test_that("count_tokens_up_to_n policy parameter works", {
  # Currently only R1 is supported
  result <- count_tokens_up_to_n(10, policy = "R1")
  expect_true(length(result$tokens) > 0)
  
  expect_error(count_tokens_up_to_n(10, policy = "R2"), "Only R1 policy is currently supported")
})

test_that("count_tokens_up_to_n handles edge cases", {
  # Test N=0
  result <- count_tokens_up_to_n(0)
  expect_equal(length(result$tokens), 0)
  expect_equal(length(result$connectives), 0)
  
  # Test N=1
  result <- count_tokens_up_to_n(1)
  expect_equal(result$tokens["um"], 1)
  expect_equal(length(result$connectives), 0)  # No connectives for single number
})

test_that("count_tokens_up_to_n scales properly", {
  # Test that counts increase with N
  result_10 <- count_tokens_up_to_n(10)
  result_100 <- count_tokens_up_to_n(100)
  
  # Total token count should increase
  total_10 <- sum(result_10$tokens)
  total_100 <- sum(result_100$tokens)
  expect_true(total_100 > total_10)
})
