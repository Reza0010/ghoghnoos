<?php
/**
 * Rayna Theme Functions
 */

// Customizer settings
require get_template_directory() . '/inc/customizer.php';

// Plugin recommendations
require get_template_directory() . '/inc/tgm-config.php';

// Sales Notifications
require get_template_directory() . '/inc/sales-notifications.php';

// Demo Import Support
require get_template_directory() . '/inc/demo-import.php';

// Admin Enhancements
require get_template_directory() . '/inc/admin-enhancements.php';

function rayna_setup() {
    // Add default posts and comments RSS feed links to head.
    add_theme_support( 'automatic-feed-links' );

    // Let WordPress manage the document title.
    add_theme_support( 'title-tag' );

    // Enable support for Post Thumbnails on posts and pages.
    add_theme_support( 'post-thumbnails' );

    // This theme uses wp_nav_menu() in one location.
    register_nav_menus( array(
        'primary' => __( 'Primary Menu', 'rayna' ),
    ) );

    // Switch default core markup for search form, comment form, and comments
    // to output valid HTML5.
    add_theme_support( 'html5', array(
        'search-form',
        'comment-form',
        'comment-list',
        'gallery',
        'caption',
    ) );

    // Custom Logo
    add_theme_support( 'custom-logo', array(
        'height'      => 50,
        'width'       => 150,
        'flex-height' => true,
        'flex-width'  => true,
    ) );

    // Custom Header
    add_theme_support( 'custom-header' );

    // Add support for WooCommerce
    add_theme_support( 'woocommerce' );
    add_theme_support( 'wc-product-gallery-zoom' );
    add_theme_support( 'wc-product-gallery-lightbox' );
    add_theme_support( 'wc-product-gallery-slider' );
}
add_action( 'after_setup_theme', 'rayna_setup' );

/**
 * Register Sidebar
 */
function rayna_widgets_init() {
    register_sidebar( array(
        'name'          => __( 'Shop Sidebar', 'rayna' ),
        'id'            => 'shop-sidebar',
        'description'   => __( 'Add widgets here to appear in your shop sidebar.', 'rayna' ),
        'before_widget' => '<section id="%1$s" class="widget %2$s mb-4">',
        'after_widget'  => '</section>',
        'before_title'  => '<h3 class="widget-title" style="font-size: 1.1rem; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 15px;">',
        'after_title'   => '</h3>',
    ) );
}
add_action( 'widgets_init', 'rayna_widgets_init' );

function rayna_scripts() {
    // Load Vazirmatn font
    wp_enqueue_style( 'rayna-fonts', 'https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;700;900&display=swap', array(), null );

    // Load FontAwesome
    wp_enqueue_style( 'font-awesome', 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css', array(), '6.4.0' );

    // Load main stylesheet
    wp_enqueue_style( 'rayna-style', get_stylesheet_uri(), array(), '1.0.0' );

    // Load scripts
    wp_enqueue_script( 'rayna-main', get_template_directory_uri() . '/assets/js/main.js', array('jquery'), '1.0.0', true );
    wp_localize_script( 'rayna-main', 'rayna_ajax', array( 'ajax_url' => admin_url( 'admin-ajax.php' ) ) );
}
add_action( 'wp_enqueue_scripts', 'rayna_scripts' );

/**
 * Remove WooCommerce Default Styles if needed for full customization
 */
// add_filter( 'woocommerce_enqueue_styles', '__return_empty_array' );

/**
 * WooCommerce Wrapper Fix
 */
function rayna_woocommerce_wrapper_start() {
    echo '<div class="container my-5">';
}
function rayna_woocommerce_wrapper_end() {
    echo '</div>';
}
remove_action( 'woocommerce_before_main_content', 'woocommerce_output_content_wrapper', 10);
remove_action( 'woocommerce_after_main_content', 'woocommerce_output_content_wrapper_end', 10);
add_action('woocommerce_before_main_content', 'rayna_woocommerce_wrapper_start', 10);
add_action('woocommerce_after_main_content', 'rayna_woocommerce_wrapper_end', 10);

/**
 * Adjust Single Product Hooks for Custom Layout
 */
remove_action( 'woocommerce_after_single_product_summary', 'woocommerce_output_product_data_tabs', 10 );

/**
 * AJAX Search Handler
 */
function rayna_ajax_search() {
    $keyword = sanitize_text_field( $_GET['keyword'] );
    $args = array(
        'post_type'      => 'product',
        'post_status'    => 'publish',
        'posts_per_page' => 5,
        's'              => $keyword,
    );
    $query = new WP_Query( $args );

    if ( $query->have_posts() ) {
        echo '<ul>';
        while ( $query->have_posts() ) {
            $query->the_post();
            global $product;
            ?>
            <li>
                <a href="<?php the_permalink(); ?>">
                    <?php the_post_thumbnail( array( 40, 40 ) ); ?>
                    <span class="title"><?php the_title(); ?></span>
                    <span class="price"><?php echo $product->get_price_html(); ?></span>
                </a>
            </li>
            <?php
        }
        echo '</ul>';
    } else {
        echo '<p>نتیجه‌ای یافت نشد.</p>';
    }
    wp_die();
}
add_action( 'wp_ajax_rayna_search', 'rayna_ajax_search' );
add_action( 'wp_ajax_nopriv_rayna_search', 'rayna_ajax_search' );
