<?php
/**
 * Rayna Theme Customizer
 */

function rayna_customize_register( $wp_customize ) {
    // Section: General Settings
    $wp_customize->add_section( 'rayna_theme_options', array(
        'title'    => __( 'تنظیمات قالب راینا', 'rayna' ),
        'priority' => 30,
    ) );

    // Setting: Primary Color
    $wp_customize->add_setting( 'rayna_primary_color', array(
        'default'           => '#007bff',
        'sanitize_callback' => 'sanitize_hex_color',
        'transport'         => 'refresh',
    ) );
    $wp_customize->add_control( new WP_Customize_Color_Control( $wp_customize, 'rayna_primary_color', array(
        'label'    => __( 'رنگ اصلی سایت', 'rayna' ),
        'section'  => 'rayna_theme_options',
        'settings' => 'rayna_primary_color',
    ) ) );

    // Setting: Footer Text
    $wp_customize->add_setting( 'rayna_footer_copy', array(
        'default'           => 'تمامی حقوق برای فروشگاه RAYNA محفوظ است.',
        'sanitize_callback' => 'sanitize_text_field',
        'transport'         => 'refresh',
    ) );
    $wp_customize->add_control( 'rayna_footer_copy', array(
        'label'    => __( 'متن کپی‌رایت فوتر', 'rayna' ),
        'section'  => 'rayna_theme_options',
        'type'     => 'text',
    ) );

    // Setting: Phone Number
    $wp_customize->add_setting( 'rayna_contact_phone', array(
        'default'           => '۰۲۱-۸۸XXXXXX',
        'sanitize_callback' => 'sanitize_text_field',
    ) );
    $wp_customize->add_control( 'rayna_contact_phone', array(
        'label'    => __( 'شماره تماس', 'rayna' ),
        'section'  => 'rayna_theme_options',
        'type'     => 'text',
    ) );
}
add_action( 'customize_register', 'rayna_customize_register' );

/**
 * Output Custom CSS based on Customizer settings
 */
function rayna_customizer_css() {
    $primary_color = get_theme_mod( 'rayna_primary_color', '#007bff' );
    ?>
    <style type="text/css">
        :root {
            --primary-color: <?php echo esc_attr( $primary_color ); ?>;
        }
        .view-all-link,
        .button.add_to_cart_button:hover,
        .footer-column h4::after,
        .category-nav ul li a:hover,
        .cart-count-badge {
            background-color: var(--primary-color) !important;
        }
        .product-info .price,
        .price ins,
        .category-nav ul li a:hover,
        .header-actions a:hover {
            color: var(--primary-color) !important;
        }
        .view-all-link {
            border-color: var(--primary-color) !important;
        }
    </style>
    <?php
}
add_action( 'wp_head', 'rayna_customizer_css' );
