<!DOCTYPE html>
<html <?php language_attributes(); ?> dir="rtl">
<head>
    <meta charset="<?php bloginfo( 'charset' ); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- SEO & Social Meta Tags -->
    <?php if ( is_single() ) : ?>
        <meta property="og:title" content="<?php the_title(); ?>">
        <meta property="og:description" content="<?php echo wp_strip_all_tags( get_the_excerpt() ); ?>">
        <meta property="og:image" content="<?php echo get_the_post_thumbnail_url( get_the_ID(), 'large' ); ?>">
        <meta property="og:url" content="<?php the_permalink(); ?>">
        <meta name="twitter:card" content="summary_large_image">
    <?php endif; ?>

    <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

    <!-- نوار بالای سایت -->
    <div class="top-banner">
        <div class="container">
            تخفیف ویژه بهاره! تا ۵۰٪ روی تمامی محصولات زنانه و مردانه 🌸
        </div>
    </div>

    <!-- هدر اصلی سایت -->
    <header>
        <div class="container">
            <div class="header-content">
                <div class="logo">
                    <?php
                    if ( has_custom_logo() ) {
                        the_custom_logo();
                    } else {
                        ?>
                        <a href="<?php echo esc_url( home_url( '/' ) ); ?>">
                            <img src="https://via.placeholder.com/150x50?text=RAYNA" alt="<?php bloginfo( 'name' ); ?>">
                        </a>
                        <?php
                    }
                    ?>
                </div>

                <div class="search-bar">
                    <i class="fas fa-search"></i>
                    <form role="search" method="get" action="<?php echo esc_url( home_url( '/' ) ); ?>" style="flex-grow:1;">
                        <input type="search" placeholder="جستجو در محصولات..." value="<?php echo get_search_query(); ?>" name="s">
                    </form>
                </div>

                <div class="header-actions">
                    <a href="#" id="login-link"><i class="far fa-user"></i></a>
                    <a href="#" id="wishlist-link">
                        <i class="far fa-heart"></i>
                        <span class="cart-count-badge" id="wishlist-count" style="display: none;">0</span>
                    </a>
                    <?php if ( class_exists( 'WooCommerce' ) ) : ?>
                    <a href="<?php echo wc_get_cart_url(); ?>">
                        <i class="fas fa-shopping-bag"></i>
                        <span class="cart-count-badge" id="cart-count"><?php echo WC()->cart->get_cart_contents_count(); ?></span>
                        <span class="cart-total-price" id="cart-total"><?php echo WC()->cart->get_cart_total(); ?></span>
                    </a>
                    <?php endif; ?>
                </div>
            </div>
        </div>
    </header>

    <!-- نوار دسته‌بندی اصلی -->
    <nav class="category-nav">
        <div class="container">
            <?php
            wp_nav_menu( array(
                'theme_location' => 'primary',
                'container'      => false,
                'menu_class'     => 'main-menu',
                'fallback_cb'    => '__return_false',
            ) );
            ?>
            <!-- Fallback static menu for demo if WP menu not set -->
            <?php if ( ! has_nav_menu( 'primary' ) ) : ?>
            <ul>
                <li><a href="#">لباس زنانه</a></li>
                <li><a href="#">لباس مردانه</a></li>
                <li><a href="#">اکسسوری</a></li>
                <li><a href="#">برندها</a></li>
                <li><a href="#">فروش ویژه</a></li>
            </ul>
            <?php endif; ?>
        </div>
    </nav>
