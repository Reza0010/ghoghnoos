jQuery(document).ready(function($) {
    // --- AJAX Search ---
    const $searchBar = $('.search-bar');
    const $searchInput = $searchBar.find('input[type="search"]');

    // Inject results container
    $searchBar.css('position', 'relative');
    $searchBar.append('<div id="rayna-search-results" style="display:none; position:absolute; top:100%; left:0; right:0; background:#fff; border:1px solid #eee; z-index:1000; box-shadow:0 10px 20px rgba(0,0,0,0.1); border-radius:0 0 8px 8px; max-height:400px; overflow-y:auto;"></div>');
    const $results = $('#rayna-search-results');

    let searchTimer;
    $searchInput.on('keyup', function() {
        const keyword = $(this).val();
        clearTimeout(searchTimer);

        if (keyword.length < 2) {
            $results.hide();
            return;
        }

        searchTimer = setTimeout(function() {
            $results.html('<p style="padding:15px; text-align:center;">در حال جستجو...</p>').show();

            $.ajax({
                url: rayna_ajax.ajax_url,
                type: 'GET',
                data: {
                    action: 'rayna_search',
                    keyword: keyword
                },
                success: function(response) {
                    $results.html(response).show();
                }
            });
        }, 500);
    });

    $(document).on('click', function(e) {
        if (!$(e.target).closest('.search-bar').length) {
            $results.hide();
        }
    });

    // --- Basic Interaction ---
    console.log('Rayna Professional Theme Initialized');
});
