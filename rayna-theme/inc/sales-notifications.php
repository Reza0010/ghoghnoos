<?php
/**
 * Sales Proof Notifications
 */

function rayna_sales_notification_html() {
    ?>
    <div id="sales-notification" class="sales-notification" style="display:none;">
        <div class="sales-notification-content">
            <img src="" alt="" class="buyer-img">
            <div class="sales-text">
                <span class="buyer-name"></span> از <span class="buyer-city"></span> <br>
                <span class="purchase-action">لحظاتی پیش این محصول را خرید</span>
            </div>
        </div>
        <button class="close-notification">&times;</button>
    </div>
    <?php
}
add_action( 'wp_footer', 'rayna_sales_notification_html' );

function rayna_localize_sales_data() {
    $data = array(
        'names' => array('علی', 'رضا', 'سارا', 'مریم', 'نیما', 'مهدی', 'الناز', 'جواد'),
        'cities' => array('تهران', 'اصفهان', 'مشهد', 'شیراز', 'تبریز', 'اهواز', 'کرمان'),
        'images' => array(
            'https://picsum.photos/seed/p1/50/50',
            'https://picsum.photos/seed/p2/50/50',
            'https://picsum.photos/seed/p3/50/50',
            'https://picsum.photos/seed/p4/50/50',
        )
    );
    wp_localize_script( 'rayna-main', 'rayna_sales_data', $data );
}
add_action( 'wp_enqueue_scripts', 'rayna_localize_sales_data', 20 );
