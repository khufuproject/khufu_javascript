Introduction
============

*khufu_javascript* provides various ways for including Javascript 
and stylesheet resources into your Khufu/Pyramid app.

Usage - Resource Registry
-------------------------

``khufu_javascript.ResourceRegistry`` is a helper utility for managing Javascript
and Stylesheet resources.

The curent *ResourceRegistry* can be looked up by calling (after including
``khufu_javascript`` with the configurator)::

  >>> from khufu_javascript import get_resource_registry
  >>> config.include('khufu_javascript')
  >>> helper = get_resource_registry(config)
  >>> helper.add_javascript('/static/foobar.js')
  >>> helper.add_stylesheet('http://someplace.com/style.css')
  >>> print 'foo'

And inside a view::

  from khufu_javascript import get_resource_registry, RequestRenderable

  @view_config('myview', renderer='templates/foo.jinja2',
               context=Root)
  def myview(request):
      helper = get_resource_registry(request)
      return {'resources': RequestRenderable(helper, request)}

  <!-- templates/foo.jinja2 -->
  <html>
    <head>
      {{ resources.render()|safe }}
    </head>
    <body>
      yes sir!
    </body>
  </html>


Usage - Dojo
------------

``khufu_javascript.dojo`` provides support for working with Dojo.

Setting up khufu_javascript.dojo is easy.
::

    # config must be an instance of pyramid.config.Configurator
    config.include('khufu_javascript.dojo')
    config.register_script_dir('myproject:javascripts')

The previous example will iterate over all *.js files in the ``javascripts``
directory relative to the ``myproject`` package (``register_script_dir`` takes
an asset spec).  For each .js file found it scans for a ``dojo.provides('foo')``
entry and registers that module with khufu_javascript.

After having registered scripts, they can be accessed via the ``dojo`` view
at the root of the site.  If one of the javascripts found has
"dojo.provides('foo.bar')" then the dojo view will provide::

    http://127.0.0.1:8080/dojo/foo/bar.js

Anyone working with Dojo modules knows that there still needs to a way
to tell Dojo to look at */dojo/whatever* when looking up non-core modules.
Dojo handles this with *djConfig* which can be used to setup module load
paths.

Here's an example.
::

    # views.py
    from khufu_javascript.dojo import get_script_registry
    from khufu_javascript import RequestRenderable

    @view_config('myview', renderer='templates/foo.jinja2',
                 context=Root)
    def myview(request):
        dojo = RequestRenderable(get_script_registry(request), request)
        return {'dojo': dojo}

    <!-- templates/foo.jinja2 -->
    <html>
      <head>
        {{ dojo.render()|safe }}
      </head>
      <body>
        yes sir!
      </body>
    </html>

The ``dojo.render()`` method will generate the appropriate *<link>*, *<style>*,
and *<script>* elements for loading Dojo.  It will also generate
the appropriate *djConfig* object that configures the module loading path
to work with our ``/dojo`` view.
