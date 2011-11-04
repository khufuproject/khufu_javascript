Introduction
============

*khufu_javascript* provides various ways for including Javascript 
and stylesheet resources into your Khufu/Pyramid app.

Usage - Resource Helper
-----------------------

``khufu_javascript.ResourceHelper`` is a helper utility for managing Javascript
and Stylesheet resources.

The curent *ResourceHelper* can be looked up by calling (after including
``khufu_javascript`` with the configurator)::

  config.include('khufu_javascript')
  helper = config.get_resource_helper()
  helper.add_javascript('myapp.js1', 'somepackage:static/foobar.js')
  helper.add_stylesheet('myapp.css1', 'somepackage:static/helloworld.css')

And inside a view::

  from khufu_javascript import ResourceHelper

  @view_config('myview', renderer='templates/foo.jinja2',
               context=Root)
  def myview(request):
      helper = ResourceHelper(request=request)
      unicode_str = helper.render()
      return {'resources_html': unicode_str}

``config.get_resource_helper()`` will always return a thread-safe *ResourceHelper*
instance so there is no need to worry about threadlocal's or global var's.


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
        {{ dojo_header|safe }}
      </head>
      <body>
        yes sir!
      </body>
    </html>

The ``render_header`` method will generate the appropriate *<link>*, *<style>*,
and *<script>* elements for loading Dojo.  It will also generate
the appropriate *djConfig* object that configures the module loading path
to work with our ``/dojo`` view.
