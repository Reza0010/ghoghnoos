<?php
/**
 * Archive Product Template
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit; // Exit if accessed directly
}

get_header( 'shop' ); ?>

<div class="container listing-page">
    <div class="listing-container" style="display: flex; gap: 30px;">

        <!-- فیلترها -->
        <aside class="filter-sidebar" style="flex: 0 0 270px; background: #fff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
            <?php if ( is_active_sidebar( 'shop-sidebar' ) ) : ?>
                <?php dynamic_sidebar( 'shop-sidebar' ); ?>
            <?php else : ?>
                <h3 style="font-size: 1.2rem; margin-bottom: 20px;">فیلترها</h3>
                <p style="color: #888; font-size: 0.9rem;">ویجت‌های فیلتر را در پنل ادمین اضافه کنید.</p>
            <?php endif; ?>
        </aside>

        <!-- لیست محصولات -->
        <main class="products-listing" style="flex: 1;">
            <header class="woocommerce-products-header" style="margin-bottom: 30px;">
                <?php if ( apply_filters( 'woocommerce_show_page_title', true ) ) : ?>
                    <h1 class="woocommerce-products-header__title page-title" style="font-size: 2rem;"><?php woocommerce_page_title(); ?></h1>
                <?php endif; ?>

                <?php
                /**
                 * Hook: woocommerce_archive_description.
                 */
                do_action( 'woocommerce_archive_description' );
                ?>
            </header>

            <?php if ( woocommerce_product_loop() ) : ?>

                <div class="shop-control-bar" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; background: #fff; padding: 15px; border-radius: 8px;">
                    <?php
                    /**
                     * Hook: woocommerce_before_shop_loop.
                     */
                    do_action( 'woocommerce_before_shop_loop' );
                    ?>
                </div>

                <?php
                woocommerce_product_loop_start();

                if ( wc_get_loop_prop( 'total' ) ) {
                    while ( have_posts() ) {
                        the_post();

                        /**
                         * Hook: woocommerce_shop_loop.
                         */
                        do_action( 'woocommerce_shop_loop' );

                        wc_get_template_part( 'content', 'product' );
                    }
                }

                woocommerce_product_loop_end();

                /**
                 * Hook: woocommerce_after_shop_loop.
                 */
                do_action( 'woocommerce_after_shop_loop' );
                ?>
            <?php else : ?>
                <?php
                /**
                 * Hook: woocommerce_no_products_found.
                 */
                do_action( 'woocommerce_no_products_found' );
                ?>
            <?php endif; ?>
        </main>
    </div>
</div>

<?php get_footer( 'shop' ); ?>
