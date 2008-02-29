$(function() {
  var sourceView = null;

  /**
   * if we are in console mode, show the console.
   */
  if (CONSOLE_MODE && EVALEX) {
    openShell(null, $('div.console div.inner').empty(), 0);
  }

  $('div.traceback div.frame').each(function() {
    var
      target = $('pre', this)
        .click(function() {
          sourceButton.click();
        }),
      consoleNode = null, source = null,
      frameID = this.id.substring(6);

    /**
     * Add an interactive console to the frames
     */
    if (EVALEX)
      $('<img src="./__debugger__?cmd=resource&f=console.png">')
        .attr('title', 'Open an interactive python shell in this frame')
        .click(function() {
          consoleNode = openShell(consoleNode, target, frameID);
          return false;
        })
        .prependTo(target);

    /**
     * Show sourcecode
     */
    var sourceButton = $('<img src="./__debugger__?cmd=resource&f=source.png">')
      .attr('title', 'Display the sourcecode for this frame')
      .click(function() {
        if (!sourceView)
          $('h2', sourceView =
            $('<div class="box"><h2>View Source</h2><div class="sourceview">' +
              '<table></table></div>')
              .insertBefore('div.explanation'))
            .css('cursor', 'pointer')
            .click(function() {
              sourceView.slideUp('fast');
            });
        $.get('./__debugger__', {cmd: 'source', frm: frameID}, function(data) {
          $('table', sourceView)
            .replaceWith(data);
          if (!sourceView.is(':visible'))
            sourceView.slideDown('fast', function() {
              document.location.href = '#current-line';
            });
          else
            document.location.href = '#current-line';
        });
        return false;
      })
      .prependTo(target);
  });

  /**
   * toggle traceback types on click.
   */
  $('h2.traceback').click(function() {
    $(this).next().slideToggle('fast');
    $('div.plain').slideToggle('fast');
  }).css('cursor', 'pointer');
  $('div.plain').hide();

  /**
   * Add extra info (this is here so that only users with JavaScript
   * enabled see it.)
   */
  $('span.nojavascript')
    .removeClass('nojavascript')
    .text('To switch between the interactive traceback and the plaintext ' +
          'one, you can click on the "Traceback" headline.  From the text ' +
          'traceback you can also create a paste of it.  For code execution ' +
          'mouse-over the frame you want to debug and click on the console ' +
          'icon on the right side.');

  /**
   * Add the pastebin feature
   */
  $('div.plain form')
    .submit(function() {
      $('input[@type="submit"]', this).val('submitting...');
      $.ajax({
        dataType:     'json',
        url:          './__debugger__',
        data:         {tb: TRACEBACK, cmd: 'paste'},
        success:      function(data) {
          console.log(data);
          $('div.plain span.pastemessage')
            .removeClass('pastemessage')
            .text('Paste created: ')
            .append($('<a>#' + data.id + '</a>').attr('href', data.url));
      }});
      return false;
    });

  // if we have javascript we submit by ajax anyways, so no need for the
  // not scaling textarea.
  var plainTraceback = $('div.plain textarea');
  plainTraceback.replaceWith($('<pre>').text(plainTraceback.text()));
});


/**
 * Helper function for shell initialization
 */
function openShell(consoleNode, target, frameID) {
  if (consoleNode)
    return consoleNode.slideDown('fast');
  consoleNode = $('<pre class="console">')
    .appendTo(target.parent())
    .hide()
  var historyPos = 0, history = [''];
  var output = $('<div class="output">[console ready]</div>')
    .appendTo(consoleNode);
  var form = $('<form>&gt;&gt;&gt; </form>')
    .submit(function() {
      var cmd = command.val();
      $.get('./__debugger__', {cmd: cmd, frm: frameID}, function(data) {
        var tmp = $('<div>').html(data);
        $('span.extended', tmp).each(function() {
          var hidden = $(this).wrap('<span>').hide();
          hidden
            .parent()
            .append($('<a href="#" class="toggle">&nbsp;&nbsp;</a>')
              .click(function() {
                hidden.toggle();
                $(this).toggleClass('open')
                return false;
              }));
        });
        output.append(tmp);
        command.focus();
        var old = history.pop();
        history.push(cmd);
        if (typeof old != 'undefined')
          history.push(old);
        historyPos = history.length - 1;
      });
      command.val('');
      return false;
    }).
    appendTo(consoleNode);

  var command = $('<input type="text">')
    .appendTo(form)
    .keypress(function(e) {
      if (e.charCode == 100 && e.ctrlKey) {
        output.text('--- screen cleared ---');
        return false;
      }
      else if (e.charCode == 0 && (e.keyCode == 38 || e.keyCode == 40)) {
        if (e.keyCode == 38 && historyPos > 0)
          historyPos--;
        else if (e.keyCode == 40 && historyPos < history.length)
          historyPos++;
        command.val(history[historyPos]);
        return false;
      }
    });
    
  return consoleNode.slideDown('fast', function() {
    command.focus();
  });
}
