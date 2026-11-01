GET_COUNTRY_QUERY = """
query GetCountry($code: ID!) {
  country(code: $code) {
    code
    name
    currency
  }
}
"""
