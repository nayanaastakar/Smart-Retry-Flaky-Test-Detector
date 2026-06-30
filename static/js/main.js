/* main.js — Smart Retry & Flaky Test Detector */
$(document).ready(function () {

  const $form      = $('#runForm');
  const $btn       = $('#runBtn');
  const $panel     = $('#outputPanel');
  const $output    = $('#consoleOutput');
  const $spinner   = $('#spinner');
  const $statusLbl = $('#statusLabel');
  const $links     = $('#resultLinks');
  const $ssPanel   = $('#screenshotPanel');
  const $ssGrid    = $('#ssGrid');
  const $ssCount   = $('#ssCount');
  const $ssEmpty   = $('#ssEmpty');

  $form.on('submit', function (e) {
    e.preventDefault();

    const websiteId  = $('#websiteConfig').val();
    const retryCount = parseInt($('#retryCount').val(), 10);
    const aiEnabled  = $('#enableAi').is(':checked');
    const headless   = $('#headlessMode').is(':checked');
    const browser    = $('#browser').val();

    if (!websiteId) {
      alert('Please select a website configuration.');
      return;
    }

    // ── show running state ────────────────────────────────────────────────
    $btn.prop('disabled', true).html('<i class="fa fa-spinner fa-spin me-2"></i>Running…');
    $panel.fadeIn(200);
    $ssPanel.hide();
    $ssGrid.empty();
    $ssEmpty.hide();
    $spinner.show();
    $statusLbl.text('Executing tests — please wait…');
    $output.text('');
    $links.hide().empty();

    $.ajax({
      url: '/api/run_tests',
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({
        website_id:  websiteId,
        retry_count: retryCount,
        ai_enabled:  aiEnabled,
        headless:    headless,
        browser:     browser,
      }),
      success: function (res) {
        $spinner.hide();
        $statusLbl.html('<i class="fas fa-check-circle text-success me-2"></i>Execution complete ✓');
        $output.text(res.output || '(no output)');

        // Build action links
        $links.empty().show();
        if (res.report_url) {
          $links.append(
            `<a href="${res.report_url}" target="_blank" class="btn btn-sm btn-primary">
               <i class="fa fa-file-code me-1"></i>HTML Report
             </a>`
          );
        }
        if (res.result_url) {
          $links.append(
            `<a href="${res.result_url}" class="btn btn-sm btn-outline-info">
               <i class="fa fa-image me-1"></i>View Evidence
             </a>`
          );
        }

        $btn.prop('disabled', false).html('<i class="fa fa-play me-2"></i>Run Tests');

        // ── Load screenshots ───────────────────────────────────────────────
        loadScreenshots();
      },
      error: function (xhr) {
        $spinner.hide();
        $statusLbl.html('<i class="fas fa-times-circle text-danger me-2"></i>An error occurred.');
        const msg = xhr.responseJSON?.error || xhr.responseText || 'Unknown error';
        $output.text('ERROR: ' + msg);
        $btn.prop('disabled', false).html('<i class="fa fa-play me-2"></i>Run Tests');
      },
    });
  });

  // ── Screenshot gallery loader ─────────────────────────────────────────────
  function loadScreenshots() {
    $.getJSON('/api/screenshots/latest', function (data) {
      const shots = data.screenshots || [];
      $ssCount.text(shots.length);
      $ssPanel.slideDown(300);

      if (shots.length === 0) {
        $ssEmpty.show();
        return;
      }

      $ssGrid.empty();
      shots.forEach(function (filename) {
        const label = filename
          .replace('.png', '')
          .replace(/_/g, ' ')
          .replace(/\b\w/g, c => c.toUpperCase());

        const src = '/screenshots/' + filename;
        const card = `
          <div class="col-xl-3 col-lg-4 col-sm-6">
            <div class="ss-run-card" onclick="openSsLightbox('${src}', '${label.replace(/'/g,"\\'")}')">
              <div class="ss-run-img-wrap">
                <img src="${src}" alt="${label}" loading="lazy"
                     onerror="this.closest('.col-xl-3,.col-lg-4,.col-sm-6').remove()">
                <div class="ss-run-overlay"><i class="fas fa-expand-alt"></i></div>
              </div>
              <div class="ss-run-caption">
                <span>${label}</span>
                <a href="${src}" download class="btn btn-xs-ss" onclick="event.stopPropagation()" title="Download">
                  <i class="fas fa-download"></i>
                </a>
              </div>
            </div>
          </div>`;
        $ssGrid.append(card);
      });
    }).fail(function () {
      $ssPanel.slideDown(300);
      $ssEmpty.show();
    });
  }
});

// ── Lightbox helper (run page) ─────────────────────────────────────────────
function openSsLightbox(src, label) {
  document.getElementById('ssLightboxImg').src = src;
  document.getElementById('ssLightboxTitle').textContent = label;
  document.getElementById('ssLightboxDownload').href = src;
  document.getElementById('ssLightboxOpen').href = src;
  new bootstrap.Modal(document.getElementById('ssLightbox')).show();
}
