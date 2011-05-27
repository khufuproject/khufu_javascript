Introduction
============

*khufu_javascript* provides various ways for including Javascript into
your Khufu/Pyramid app.

Dojo Support
============

``khufu_javascript.dojo`` provides support for working with Dojo.

Usage
-----

Setting up khufu_javascript.dojo is easy.
::

    # config must be an instance of pyramid.config.Configurator
    config.include('khufu_javascript.dojo')
    config.register_script_dir('myproject:javascripts')

The previous example will iterate over all *.js files in the ``javascripts``
directory relative to the ``myproject`` package (``register_script_dir`` takes
an asset spec).  For each .js file found it scans for a "dojo.provides('foo')"
entry and registers that module with khufu_javascript.

After having registered scripts, they can be accessed via the ``dojo`` view
at the root of the site.  If one of the javascripts found has
"dojo.provides('foo.bar')" then the dojo view will provide::

    http://127.0.0.1:8080/dojo/foo/bar.js

Anyone working with Dojo modules knows that there still needs to a way
to tell Dojo to look at */dojo/whatever* when looking up non-core modules.
Dojo handles this with *djConfig* which can be used to setup module load
paths.

After having registered scripts, inside of your views you can simply call
``khufu_javascript.dojo.render_header``.
::

    # views.py
    from khufu_javascript.dojo import render_header

    @view_config('myview', renderer='templates/foo.jinja2',
                 context=Root)
    def myview(request):
        dojo_header = render_header(request)
        return {'dojo_header': dojo_header}

    <!-- templates/foo.jinja2 -->
    <html>
      <head>
        {{ dojo_header }}
      </head>
      <body>
        yes sir!
      </body>
    </html>

The ``render_header`` method will generate the appropriate *<link>*, *<style>*,
and *<script>* elements for loading Dojo.  It will also generate
the appropriate *djConfig* object that configures the module loading path
to work with our /dojo view.
