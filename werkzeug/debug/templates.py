# -*- coding: utf-8 -*-
"""
    werkzeug.debug.templates
    ~~~~~~~~~~~~~~~~~~~~~~~~

    JavaScript, CSS and HTML that is part of the traceback debugger.

    :copyright: 2007 by Georg Brandl, Armin Ronacher, Benjamin Wiegand.
    :license: BSD, see LICENSE for more details.
"""

JAVASCRIPT = r'''
function toggleBlock(handler) {
    if (handler.nodeName == 'H3') {
        var table = handler;
        do {
            table = table.nextSibling;
            if (typeof table == 'undefined') {
                return;
            }
        }
        while (table.nodeName != 'TABLE');
    }

    else if (handler.nodeName == 'DT') {
        var parent = handler.parentNode;
        var table = parent.getElementsByTagName('TABLE')[0];
    }

    var lines = table.getElementsByTagName("TR");
    for (var i = 0; i < lines.length; i++) {
        var line = lines[i];
        if (line.className == 'pre' || line.className == 'post') {
            line.style.display = (line.style.display == 'none') ? '' : 'none';
        }
        else if (line.parentNode.parentNode.className == 'vars' ||
                 line.parentNode.parentNode.className == 'exec_code') {
            line.style.display = (line.style.display == 'none') ? '' : 'none';
            var input = line.getElementsByTagName('TEXTAREA');
            if (input.length) {
                input[0].focus();
            }
        }
    }
}

function initTB() {
    var tb = document.getElementById('wsgi-traceback');
    var handlers = tb.getElementsByTagName('H3');
    for (var i = 0; i < handlers.length; i++) {
        toggleBlock(handlers[i]);
        handlers[i].setAttribute('onclick', 'toggleBlock(this)');
    }
    handlers = tb.getElementsByTagName('DT');
    for (var i = 0; i < handlers.length; i++) {
        toggleBlock(handlers[i]);
        handlers[i].setAttribute('onclick', 'toggleBlock(this)');
    }
    var handlers = tb.getElementsByTagName('TEXTAREA');
    for (var i = 0; i < handlers.length; i++) {
        var hid = handlers[i].getAttribute('id');
        if (hid && hid.substr(0, 6) == 'input-') {
            var p = handlers[i].getAttribute('id').split('-');
            handlers[i].onkeyup = makeEnter(p[1], p[2]);
        }
    }
}

AJAX_ACTIVEX = ['Msxml2.XMLHTTP', 'Microsoft.XMLHTTP', 'Msxml2.XMLHTTP.4.0'];

function ajaxConnect() {
    var con = null;
    try {
        con = new XMLHttpRequest();
    }
    catch (e) {
        if (typeof AJAX_ACTIVEX == 'string') {
            con = new ActiveXObject(AJAX_ACTIVEX);
        }
        else {
            for (var i=0; i < AJAX_ACTIVEX.length; i++) {
                var axid = AJAX_ACTIVEX[i];
                try {
                    con = new ActiveXObject(axid);
                }
                catch (e) {}
                if (con) {
                    AJAX_ACTIVEX = axid;
                    break;
                }
            }
        }
    }
    return con;
}

function execCode(traceback, frame) {
    var input = document.getElementById('input-' + traceback + '-' +
                                        frame);
    var e = encodeURIComponent;
    var data = 'tb=' + e(traceback) + '&' +
               'frame=' + e(frame) + '&' +
               'code=' + e(input.value);
    writeToOutput(traceback, frame, '>>> ' + input.value);
    var con = ajaxConnect();
    con.onreadystatechange = function() {
        if (con.readyState == 4) {
            writeToOutput(traceback, frame, con.responseText);
            input.focus();
        }
    };
    con.open('GET', '__traceback__?' + data, true);
    con.send(null);
}

function makeEnter(traceback, frame) {
    return function(e) {
        var e = (e) ? e : window.event;
        var code = (e.keyCode) ? e.keyCode : e.which;
        if (code == 13) {
            var input = document.getElementById('input-' + traceback +
                                                '-' + frame);
            if (input.className == 'big') {
                if (input.value.substr(input.value.length - 2) != '\n\n') {
                    return;
                }
                input.value = input.value.substr(0, input.value.length - 1);
                input.className = 'small';
            }
            if (input.value == 'clear\n') {
                clearOutput(traceback, frame);
                input.value = '';
            }
            else {
                execCode(traceback, frame);
                input.value = '';
            }
        }
    }
}

function writeToOutput(traceback, frame, text) {
    var output = document.getElementById('output-' + traceback + '-' +
                                         frame);
    if (text && text != '\n') {
        var node = document.createTextNode(text);
        output.appendChild(node);
    }
}

function clearOutput(traceback, frame) {
    var output = document.getElementById('output-' + traceback + '-' +
                                         frame);
    output.innerHTML = '';
}

function toggleExtend(traceback, frame) {
    var input = document.getElementById('input-' + traceback + '-' +
                                        frame);
    input.className = (input.className == 'small') ? 'big' : 'small';
    input.focus();
}

function change_tb() {
    interactive = document.getElementById('interactive');
    plain = document.getElementById('plain');
    interactive.style.display = ((interactive.style.display == 'block') | (interactive.style.display == '')) ? 'none' : 'block';
    plain.style.display = (plain.style.display == 'block') ? 'none' : 'block';
}
'''

STYLESHEET = '''
body {
  font-size:0.9em;
  margin: 0;
  padding: 1.3em;
}

* {
  margin:0;
  padding:0;
}

#wsgi-traceback {
  margin: 1em;
  border: 1px solid #5F9CC4;
  background-color: #F6F6F6;
}

.footer {
  margin: 1em;
  font-size: 0.9em;
  letter-spacing: 0.1em;
  color: #555;
  text-align: right;
}

.footer .arthur {
  font-weight: bold;
}

h1 {
  background-color: #3F7CA4;
  font-size:1.2em;
  color:#FFFFFF;
  padding:0.3em;
  margin:0 0 0.2em 0;
}

h2 {
  background-color:#5F9CC4;
  font-size:1em;
  color:#FFFFFF;
  padding:0.3em;
  margin:0.4em 0 0.2em 0;
}

h2.tb {
  cursor:pointer;
}

h3 {
  font-size:1em;
  cursor:pointer;
}

h3.fn {
  margin-top: 0.5em;
  padding: 0.3em;
}

h3.fn:hover {
  color: #777;
}

h3.indent {
  margin:0 0.7em 0 0.7em;
  font-weight:normal;
}

p.text {
  padding:0.1em 0.5em 0.1em 0.5em;
}

p.errormsg {
  padding:0.1em 0.5em 0.1em 0.5em;
  font-size: 16px;
}

p.errorline {
  padding:0.1em 0.5em 0.1em 2em;
  font-size: 14px;
}

div.frame {
  margin: 0 2em 0 1em;
}

table.code {
  margin: 0.4em 0 0 0.5em;
  background-color:#E0E0E0;
  width:100%;
  font-family: monospace;
  font-size:13px;
  border:1px solid #C9C9C9;
  border-collapse:collapse;
}

table.code td.lineno {
  width:42px;
  text-align:right;
  padding:0 5px 0 0;
  color:#444444;
  font-weight:bold;
  border-right:1px solid #888888;
}

table.code td.code {
  background-color:#EFEFEF;
  padding:1px 0 1px 5px;
  white-space:pre;
}

table.code tr.cur td.code {
  background-color: #fff;
  border-top: 1px solid #ccc;
  border-bottom: 1px solid #ccc;
  white-space: pre;
}

pre.plain {
  margin:0.5em 1em 1em 1em;
  padding:0.5em;
  border:1px solid #999999;
  background-color: #FFFFFF;
  font-family: monospace;
  font-size: 13px;
}

table.exec_code {
  width:100%;
  margin:0 1em 0 1em;
}

table.exec_code td.input {
  width:100%;
}

table.exec_code textarea.small {
  width:100%;
  height:1.5em;
  border:1px solid #999999;
}

table.exec_code textarea.big {
  width:100%;
  height:5em;
  border:1px solid #999999;
}

table.exec_code input {
  height:1.5em;
  border:1px solid #999999;
  background-color:#FFFFFF;
}

table.exec_code td.extend {
  width:70px;
  padding:0 5px 0 5px;
}

table.exec_code td.output pre {
  font-family: monospace;
  white-space: pre-wrap;       /* css-3 should we be so lucky... */
  white-space: -moz-pre-wrap;  /* Mozilla, since 1999 */
  white-space: -pre-wrap;      /* Opera 4-6 ?? */
  white-space: -o-pre-wrap;    /* Opera 7 ?? */
  word-wrap: break-word;       /* Internet Explorer 5.5+ */
  _white-space: pre;   /* IE only hack to re-specify in addition to word-wrap  */
}

table.vars {
  margin:0 1.5em 0 1.5em;
  border-collapse:collapse;
  font-size: 0.9em;
}

table.vars td {
  font-family: 'Bitstream Vera Sans Mono', 'Courier New', monospace;
  padding: 0.3em;
  border: 1px solid #ddd;
  vertical-align: top;
  background-color: white;
}

table.vars .name {
  font-style: italic;
}

table.vars .value {
  color: #555;
}

table.vars th {
  padding: 0.2em;
  border: 1px solid #ddd;
  background-color: #f2f2f2;
  text-align: left;
}

#plain {
  display: none;
}

dl dt {
  padding: 0.2em 0 0.2em 1em;
  font-weight: bold;
  cursor: pointer;
  background-color: #ddd;
}

dl dt:hover {
  background-color: #bbb; color: white;
}

dl dd {
  padding: 0 0 0 2em;
  background-color: #eee;
}

span.p-kw {
  font-weight: bold;
  color: #008800;
}

span.p-cmt {
  color: #888888;
}

span.p-str {
  color: #dd2200;
  background-color: #fff0f0;
}

span.p-num {
  color: #0000DD;
  font-weight: bold;
}

span.p-op {
  color: black;
}
'''
