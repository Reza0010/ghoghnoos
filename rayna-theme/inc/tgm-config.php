<?php
/**
 * TGM Plugin Activation Config
 * Note: For a real production theme, include class-tgm-plugin-activation.php
 */

function rayna_register_required_plugins() {
    $plugins = array(
        array(
            'name'      => 'WooCommerce',
            'slug'      => 'woocommerce',
            'required'  => true,
        ),
        array(
            'name'      => 'Rank Math SEO',
            'slug'      => 'seo-by-rank-math',
            'required'  => false,
        ),
        array(
            'name'      => 'Elementor Website Builder',
            'slug'      => 'elementor',
            'required'  => false,
        ),
        array(
            'name'      => 'ZarinPal Gateway for WooCommerce',
            'slug'      => 'zarinpal-woocommerce-payment-gateway',
            'required'  => false,
        ),
    );

    // In a real theme, you'd call tgmpa( $plugins, $config );
    // For now, let's just show a simple admin notice if WooCommerce is missing.
    if ( ! class_exists( 'WooCommerce' ) ) {
        add_action( 'admin_notices', function() {
            echo '<div class="notice notice-warning is-dismissible"><p>قالب راینا برای عملکرد صحیح به افزونه <strong>ووکامرس</strong> نیاز دارد. لطفاً آن را نصب کنید.</p></div>';
        } );
    }
}
add_action( 'init', 'rayna_register_required_plugins' );
