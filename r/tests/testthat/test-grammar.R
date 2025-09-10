# Tests for grammar module

test_that("text_number generates basic number words", {
  expect_equal(text_number(1), "um")
  expect_equal(text_number(2), "dois")
  expect_equal(text_number(3), "três")
  expect_equal(text_number(10), "dez")
  expect_equal(text_number(11), "onze")
})

test_that("text_number generates tens correctly", {
  expect_equal(text_number(20), "vinte")
  expect_equal(text_number(21), c("vinte", "e", "um"))
  expect_equal(text_number(30), "trinta")
  expect_equal(text_number(31), c("trinta", "e", "um"))
})

test_that("text_number generates hundreds correctly", {
  expect_equal(text_number(100), "cem")
  expect_equal(text_number(101), c("cento", "e", "um"))
  expect_equal(text_number(200), "duzentos")
  expect_equal(text_number(201), c("duzentos", "e", "um"))
})

test_that("text_number generates thousands correctly", {
  expect_equal(text_number(1000), "mil")
  expect_equal(text_number(1001), c("mil", "e", "um"))
  expect_equal(text_number(2000), c("dois", "mil"))
  expect_equal(text_number(2001), c("dois", "mil", "e", "um"))
})

test_that("text_number generates millions correctly", {
  expect_equal(text_number(1000000), c("um", "milhão"))
  expect_equal(text_number(2000000), c("dois", "milhões"))
})

test_that("text_number handles edge cases", {
  expect_equal(text_number(0), "zero")
  expect_error(text_number(-1), "n must be non-negative")
  expect_error(text_number(1, policy = "invalid"), "Only R1 policy is currently supported")
})

test_that("text_number places connectives correctly", {
  # Test "e" connective in various positions
  result <- text_number(21)
  expect_true("e" %in% result)
  expect_equal(which(result == "e"), 2)  # "e" should be between tens and units
  
  result <- text_number(101)
  expect_true("e" %in% result)
  expect_equal(which(result == "e"), 2)  # "e" should be between hundreds and units
})

test_that("text_number is consistent", {
  # Test that the same number always generates the same tokens
  for (n in 1:100) {
    result1 <- text_number(n)
    result2 <- text_number(n)
    expect_equal(result1, result2)
  }
})

test_that("text_number policy parameter works", {
  # Currently only R1 is supported
  expect_equal(text_number(21, policy = "R1"), c("vinte", "e", "um"))
  expect_error(text_number(21, policy = "R2"), "Only R1 policy is currently supported")
})
