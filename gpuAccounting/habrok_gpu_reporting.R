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

#' Report Habrok GPU statistics
#'
#' @param sacct_data A table, as returned by `sacct`
#'
#' @return A data table with three columns:
#'   *
#' @export
#'
#' @author Pedro Santos Neves
#'
#' @examples
habrok_gpu_stats <- function(sacct_data, gpu_type) {


  # Remove duplicate entries (those have non-numeric JobIDs)
  habrok_gpu_stats_pruned <- sacct_data |> na.omit() |>
    dplyr::filter(grepl("[0-9]$", JobID)) |>
    dplyr::distinct()

  testit::assert(fact = "There are no duplicates",
                 identical(length(unique(habrok_gpu_stats_pruned$JobID)),
                           nrow(habrok_gpu_stats_pruned)))
  testit::assert(
    fact = "Only counting GPU nodes",
    all(grepl("v100|a100", as.character(habrok_gpu_stats_pruned$NodeList)))
  )

  #Split the data by card type
  habrok_gpu_stats_a100 <- habrok_gpu_stats_pruned |> na.omit() |>
    dplyr::filter(grepl("a100", NodeList)) |>
    dplyr::distinct()

  habrok_gpu_stats_v100 <- habrok_gpu_stats_pruned |> na.omit() |>
    dplyr::filter(grepl("v100", NodeList)) |>
    dplyr::distinct()

  # Some jobs request A100s and V100s. Now we only want one type, so we count
  # how many occurrences of "a100" and "v100" there are when we detect
  # an A100 in the V100 data set and vice versa
  habrok_gpu_stats_v100$AllocNodes <-
    ifelse(
      grepl("a100", habrok_gpu_stats_v100$NodeList),
      stringr::str_count(
        string = as.character(habrok_gpu_stats_v100$NodeList),
        "v100"
      ),
      habrok_gpu_stats_v100$AllocNodes
    )

  habrok_gpu_stats_a100$AllocNodes <-
    ifelse(
      grepl("v100", habrok_gpu_stats_a100$NodeList),
      stringr::str_count(
        string = as.character(habrok_gpu_stats_a100$NodeList),
        "a100"),
      habrok_gpu_stats_a100$AllocNodes
    )

  # Account for jobs requesting > 1 GPU node
  total_time_seconds <- sum(
    habrok_gpu_stats_pruned$ElapsedRaw * habrok_gpu_stats_pruned$AllocNodes
  )

  a100_time_seconds <- sum(
    habrok_gpu_stats_a100$ElapsedRaw * habrok_gpu_stats_a100$AllocNodes
  )

  v100_time_seconds <- sum(
    habrok_gpu_stats_v100$ElapsedRaw * habrok_gpu_stats_v100$AllocNodes
  )


  total_time_period <- lubridate::seconds_to_period(total_time_seconds)
  a100_time_period <- lubridate::seconds_to_period(a100_time_seconds)
  v100_time_period <- lubridate::seconds_to_period(v100_time_seconds)
  out <- data.frame(
    total_time_period = total_time_period,
    a100_time_period = a100_time_period,
    v100_time_period = v100_time_period
  )
  out
}
