source_with_additional_code <- function(file_path, prefix_code = '', postfix_code = '', env = new.env()) {
    file_content <- readChar(file_path, nchars = file.info(file_path)$size)
    combined_code <- paste(prefix_code, file_content, postfix_code, sep = "\n")

    text_conn <- textConnection(combined_code)
    source(text_conn, env)
    close(text_conn)

    return(env)
}

source_solution <- function(prefix_code = '', postfix_code = '') {
    env <- source_with_additional_code(file_path='solution.R', prefix_code, postfix_code)
    return(env)
}

source_submission <- function(prefix_code = '', postfix_code = '') {
    env <- source_with_additional_code(file_path='/grade/student/submission.R', prefix_code, postfix_code)
    return(env)
}