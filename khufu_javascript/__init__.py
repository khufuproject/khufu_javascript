from pyramid.events import BeforeRender

from ._api import (ResourceRegistry, get_resource_registry,
                   JavascriptResource, StylesheetResource,
                   RequestRenderable)


def setup_resources(event):
    request = event['request']
    event['khufu_resources'] = RequestRenderable(
        get_resource_registry(request), request)


def includeme(c):
    c.add_subscriber(setup_resources, BeforeRender)
