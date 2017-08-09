components = {'login_1': {'params': ['pass']},
              'login_2': {'params': ['other', 'foo']}
};

n_pages = 0;

if (typeof page_name === 'undefined') {
  throw "Must set the 'page_name' variable before importing this library."
}

// Fill in the hidden page_n if it exists.
$('#page_n').val(next_page_n());


function add_page(){
  // Add a page to be configured.
  n_pages += 1;
  r = $('<div/>', {
          class: 'card',
          style: 'max-width: 80%; margin-left: 3em; margin-bottom: 2em;'
      }).appendTo($('#parameters'));

  input_div = $('<div/>', {
                  id: 'form' + n_pages + '_div',
                  class: 'card-block',
               }).appendTo(r);
  row = $('<div/>', {
            class: 'row'
        }).appendTo(input_div);
  ppp = $('<div/>', {
            class: 'col-4'
        }).appendTo(row);
  fff = $('<form/>', {
            id: 'form' + n_pages,
            method: 'get',
            action: 'javascript: log_forms();'
        }).appendTo(ppp);
  fff.data('page_n', n_pages)
  sss = $('<select/>', {
            id: 'form' + n_pages + '_pagename',
            class: 'custom-select'
        }).appendTo(fff);
  sss.data('page_n', n_pages)
  ppp = $('<div/>', {
            id: 'form' + n_pages + '_parameters',
            class: "col-8"
        }).appendTo(row);


  for (var i = 0; i < Object.keys(components).length; i++) {
    key = Object.keys(components)[i]
    sss.append($("<option></option>")
                    .attr("value", key)
                    .text(key));
  }
  // Register the change handler for the newly created select.
  sss.change(select_changed);
  // Trigger the form creation to fire
  sss.val(Object.keys(components)[0]).change();
}

function page_html(page_name, form_n, element){
  config = components[page_name];
  if (config === undefined){
    console.log('Page not found...')
  }

  for (var i = 0; i < config['params'].length; i++) {
    name = config['params'][i];

    r = $('<div/>', {
            id: 'foo',
            class: 'form-group row',
        }).appendTo(element);

    r.append('<label for="form' + form_n + '_' + name + '" class="col-sm-2 col-form-label">' + name);

    input_div = $('<div/>', {
                    class: 'col-sm-10',
                 }).appendTo(r);

    input_div.append('<input type="text" form="form' + form_n + '" class="form-control" id="form' + form_n + '_' + name + '" placeholder="' + name + '">')
  };
}

function select_changed(event) {
  page = event.target.value;
  container = $(event.target).parent();
  var page_num = $(event.target).data('page_n');

  params = $('#form' + page_num + '_parameters')
  params.empty();
  page_html(page, page_num, params);
}

function config_options(){
  f = $('input[name=balance]:checked');
  auth_config = [];
  provider_configuration = {accounts: {'page': $('input[name=accounts]:checked').val()},
                            balance: {'page': $('input[name=balance]:checked').val()},
                            auth: auth_config}

  for (var i = 1; i <= n_pages; i++) {
    page_configuration = {'page': $('#form' + i + '_pagename').val()}
    auth_config.push(page_configuration);

    inputs = $(':input[form="form' + i + '"]')
    inputs.each(function(i, item){

      item = $(item);
      key = item.attr('placeholder');
      page_configuration[key] = item.val();
    });

  }
  return provider_configuration
}

function config_url(){
    provider_configuration = session_config();
    return 'start.html?configJSON=' + encodeURIComponent(JSON.stringify(provider_configuration));
}

function log_forms(){
  provider_configuration = config_options()
  // Save data to sessionStorage
  sessionStorage.setItem('provider_config', JSON.stringify(provider_configuration));
}

function store_session() {
  log_forms();
  $('#main').attr('action', next_page());
  return true;
}


// Read a page's GET URL variables and return them as an associative array.
function getUrlVars()
{
  var qd = {};
  if (location.search) location.search.substr(1).split("&").forEach(function(item) {
    var s = item.split("="),
        k = s[0],
        v = s[1] && decodeURIComponent(s[1]); //  null-coalescing / short-circuit
    //(k in qd) ? qd[k].push(v) : qd[k] = [v]
    (qd[k] = qd[k] || []).push(v) // null-coalescing / short-circuit
  })
  return qd
}


function page_n() {
  page_n_v = getUrlVars()['page_n']
  if (page_n_v === undefined) {
    if (page_name == 'start') {
      page_n_v = 0
    } else {
      // TODO: Make this the index page?
      //$(location).attr('href', 'start.html')
    }
  }
  return parseInt(page_n_v)
}


function next_page_n() {
  return page_n() + 1
}


function next_page(){
  i = next_page_n()
  if (i - 1 == total_n_pages()) {
    conf = session_config()
    next = conf['balance']['page'] + '.html'
  } else {
    config = page_config(i)
    next = config['page'] + '.html?page_n=' + i
  }
  return next
}

function session_config(){
  // Get saved data from sessionStorage
  var data = sessionStorage.getItem('provider_config');

  if (!data) {
    // TODO: Make this the index page?
    if (page_name != 'start') {
      $(location).attr('href', 'start.html');
    } else {
      throw "No session data"
    }
  }
  session_config_v = JSON.parse(data);
  return session_config_v
}

function page_config(i){
  return session_config()['auth'][i - 1];
}

function form_action(){
  var data = sessionStorage.getItem('provider_config');
}

function total_n_pages(){
  // Get saved data from sessionStorage
  var data = sessionStorage.getItem('provider_config');

  if (data) {
    session_config_v = JSON.parse(data);
    return session_config_v['auth'].length
  } else {
    return 0;
  }
}




// Setup the page itself.

function syntaxHighlight(json) {
  json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
      var cls = 'number';
      if (/^"/.test(match)) {
          if (/:$/.test(match)) {
              cls = 'key';
          } else {
              cls = 'string';
          }
      } else if (/true|false/.test(match)) {
          cls = 'boolean';
      } else if (/null/.test(match)) {
          cls = 'null';
      }
      return '<span class="' + cls + '">' + match + '</span>';
  });
}

function global_onready() {
  body = $('body')
  $('<div/>', {id: 'header'}).prependTo(body).html(`
    <ul class="nav justify-content-end">
      <li class="nav-item">
        <a class="nav-link active" href="#">Active</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="#">Link</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="#">Link</a>
      </li>
      <li class="nav-item">
        <a class="nav-link disabled" href="#">Disabled</a>
      </li>
    </ul>
    <ol class="breadcrumb">
      <li class="breadcrumb-item"><a href="https://pyggybank.github.io/">pyggybank</a></li>
      <li class="breadcrumb-item"><a href="start.html">testing</a></li>
    </ol>
    <div class="alert alert-info" role="alert">
      <strong>Note</strong> This page is part of pyggybank's testing suite.
      It is intended to be a place where the different types of internet banking
      providers may be tested. All data in these pages is manufactured for testing
      only.
    </div>
`);

  if (!sessionStorage.getItem('provider_config')) {
    footer = 'not set'
  } else {
    // TODO: Use the utility to get this value.
    config = JSON.stringify(JSON.parse(sessionStorage.getItem('provider_config')), null, 2);

    footer = `
    <!-- Button trigger modal -->
    <button type="button" class="btn btn-primary" data-toggle="modal" data-target="#configJSON">
      set
    </button>

    <a href="` + config_url() + `">Config URL</a>

    <!-- Modal -->
    <div class="modal fade" id="configJSON" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="exampleModalLabel">Test Provider Config</h5>
            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <pre id="config-json">` + syntaxHighlight(config) + `</pre>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>
    `
  }

  $('<footer/>', {id: 'footer', 'class': 'footer bd-footer'}).appendTo(body)
    .html('Config: ' + footer);
}

// TODO: I question if this is *really* desirable.
$( document ).ready(global_onready);
