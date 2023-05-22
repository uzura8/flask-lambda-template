from urllib.parse import urlparse


def join_query(url, add_query=''):
    parsed = urlparse(url)

    queries = []
    if parsed.query:
        queries.append(parsed.query)
    if add_query:
        queries.append(add_query)

    query = ''
    if queries:
        query = '&'.join(queries)
    if query:
        query = '?' + query

    fragment = ''
    if parsed.fragment:
        fragment = '#' + parsed.fragment

    items = [
        parsed.scheme,
        '://',
        parsed.netloc,
        parsed.path,
        query,
        fragment,
    ]
    return ''.join(items)
