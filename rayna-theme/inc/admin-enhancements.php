<?php
/**
 * Rayna Pro Admin Enhancements
 */

/**
 * 1. Custom Dashboard Widget for Shop Reports
 */
function rayna_add_dashboard_widgets() {
    if ( class_exists( 'WooCommerce' ) ) {
        wp_add_dashboard_widget(
            'rayna_shop_reports_widget',
            'گزارش سریع فروشگاه راینا',
            'rayna_dashboard_widget_content'
        );
    }
}
add_action( 'wp_dashboard_setup', 'rayna_add_dashboard_widgets' );

function rayna_dashboard_widget_content() {
    $total_sales = wc_format_decimal( get_option( 'woocommerce_total_sales' ), 0 );
    $order_count = wp_count_posts( 'shop_order' );
    $low_stock = wc_get_products( array( 'stock_status' => 'outofstock', 'limit' => -1 ) );

    ?>
    <div class="rayna-admin-stats" style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-right: 4px solid #007bff;">
            <span style="display:block; font-size: 0.8rem; color: #666;">کل فروش</span>
            <strong style="font-size: 1.2rem; color: #333;"><?php echo number_format($total_sales); ?> <small>تومان</small></strong>
        </div>
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-right: 4px solid #27ae60;">
            <span style="display:block; font-size: 0.8rem; color: #666;">تعداد سفارشات</span>
            <strong style="font-size: 1.2rem; color: #333;"><?php echo $order_count->publish; ?></strong>
        </div>
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-right: 4px solid #e74c3c;">
            <span style="display:block; font-size: 0.8rem; color: #666;">محصولات ناموجود</span>
            <strong style="font-size: 1.2rem; color: #333;"><?php echo count($low_stock); ?></strong>
        </div>
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-right: 4px solid #f39c12;">
            <span style="display:block; font-size: 0.8rem; color: #666;">نسخه قالب</span>
            <strong style="font-size: 1.2rem; color: #333;">1.5.0 PRO</strong>
        </div>
    </div>
    <div style="margin-top: 15px; text-align: center;">
        <a href="<?php echo admin_url('admin.php?page=wc-reports'); ?>" class="button button-primary">مشاهده گزارشات کامل</a>
    </div>
    <?php
}

/**
 * 2. Custom Login Page Branding
 */
function rayna_custom_login_logo() {
    $custom_logo_id = get_theme_mod( 'custom_logo' );
    $logo = wp_get_attachment_image_src( $custom_logo_id , 'full' );
    $logo_url = $logo ? $logo[0] : 'https://via.placeholder.com/150x50?text=RAYNA';
    ?>
    <style type="text/css">
        #login h1 a, .login h1 a {
            background-image: url(<?php echo $logo_url; ?>);
            height: 60px;
            width: 100%;
            background-size: contain;
            background-repeat: no-repeat;
            padding-bottom: 20px;
        }
        body.login {
            background-color: #f4f4f4;
            display: flex;
            align-items: center;
        }
        .login form {
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1) !important;
            border: none !important;
        }
        .wp-core-ui .button-primary {
            background: #007bff !important;
            border-color: #007bff !important;
            text-shadow: none !important;
            border-radius: 6px !important;
        }
    </style>
    <?php
}
add_action( 'login_enqueue_scripts', 'rayna_custom_login_logo' );

function rayna_login_logo_url() {
    return home_url();
}
add_filter( 'login_headerurl', 'rayna_login_logo_url' );

/**
 * 3. Enhance Product List in Admin
 */
function rayna_add_product_admin_columns($columns) {
    $new_columns = array();
    foreach($columns as $key => $value) {
        if ($key == 'name') {
            $new_columns['rayna_thumb'] = 'تصویر';
        }
        $new_columns[$key] = $value;
    }
    return $new_columns;
}
add_filter('manage_edit-product_columns', 'rayna_add_product_admin_columns');

function rayna_product_admin_column_content($column, $post_id) {
    if ($column == 'rayna_thumb') {
        echo get_the_post_thumbnail($post_id, array(50, 50));
    }
}
add_action('manage_product_posts_custom_column', 'rayna_product_admin_column_content', 10, 2);

/**
 * 4. Admin Bar Quick Links
 */
function rayna_admin_bar_links( $wp_admin_bar ) {
    $wp_admin_bar->add_node( array(
        'id'    => 'rayna_links',
        'title' => 'راینا پرو',
        'href'  => '#',
        'meta'  => array( 'class' => 'rayna-toolbar-icon' ),
    ) );

    $wp_admin_bar->add_node( array(
        'id'     => 'rayna_customize',
        'parent' => 'rayna_links',
        'title'  => 'تنظیمات قالب',
        'href'   => admin_url( 'customize.php' ),
    ) );

    if ( class_exists( 'WooCommerce' ) ) {
        $wp_admin_bar->add_node( array(
            'id'     => 'rayna_new_product',
            'parent' => 'rayna_links',
            'title'  => 'افزودن محصول جدید',
            'href'   => admin_url( 'post-new.php?post_type=product' ),
        ) );
    }
}
add_action( 'admin_bar_menu', 'rayna_admin_bar_links', 999 );
