#' Read `sacct` output
#'
#' @param path Path to file to read.
#'
#' @return 5 column tibble with JobID, ElapsedRaw, AllocNodes, NodeList,
#'   AllocTres
#' @export
#' @author Pedro Santos Neves
#'
#'
#' @examples
read_sacct <- function(path) {
  sacct_data <- readr::read_delim(
    file = path,
    delim = "|",
    escape_double = FALSE,
    col_types = readr::cols(
      JobID = readr::col_character(),
      ElapsedRaw = readr::col_double(),
      AllocNodes = readr::col_integer(),
      NodeList = readr::col_factor(),
      AllocTRES = readr::col_character(),
      ...6 = readr::col_skip()),
    trim_ws = TRUE
  )
  testit::assert(
    "Correct columns are available",
    identical(
      colnames(sacct_data),
      c("JobID", "ElapsedRaw", "AllocNodes", "NodeList", "AllocTRES" )
    )
  )
  testit::assert("Data has entries", nrow(sacct_data) > 0)
  sacct_data
}
