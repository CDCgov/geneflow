

import sys

from geneflow.uri_parser import URIParser



@given('I have a URI')
def step_impl(context):

    context.uris = {}
    for row in context.table:
        context.uris[row['uri']] = {}


@when('I parse the URI')
def step_impl(context):

    for uri in context.uris:
        parsed_uri = URIParser.parse(uri)
        assert parsed_uri
        context.uris[uri] = parsed_uri


@then('I see the following parsed components')
def step_impl(context):

    for row in context.table:
        assert row['uri'] in context.uris
        assert row['chopped_uri'] == context.uris[row['uri']]['chopped_uri']
        assert row['scheme'] == context.uris[row['uri']]['scheme']
        assert row['authority'] == context.uris[row['uri']]['authority']
        assert row['path'] == context.uris[row['uri']]['path']
        assert row['chopped_path'] == context.uris[row['uri']]['chopped_path']
        assert row['folder'] == context.uris[row['uri']]['folder']
        assert row['name'] == context.uris[row['uri']]['name']


@when('I switch the URI context to "{new_base_uri}"')
def step_impl(context, new_base_uri):

    for uri in context.uris:
        new_uri = URIParser.switch_context(uri, new_base_uri)
        assert new_uri
        context.uris[uri] = new_uri


@then('I see the following switched URIs')
def step_impl(context):

    for row in context.table:
        print(row['uri'], row['switched_uri'], context.uris[row['uri']]['uri'])
        assert row['uri'] in context.uris
        assert row['switched_uri'] == context.uris[row['uri']]['uri']


