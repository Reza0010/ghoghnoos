<?php
/**
 * Single Product Template
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit; // Exit if accessed directly
}

get_header( 'shop' ); ?>

<main class="container my-5">
    <?php while ( have_posts() ) : the_post(); ?>

        <div id="product-<?php the_ID(); ?>" <?php wc_product_class( 'product-single-wrapper', $product ); ?> style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 30px;">

            <!-- راست: بخش خرید و قیمت -->
            <section class="purchase-options" style="background: #fff; padding: 25px; border-radius: 12px; border: 1px solid #eee;">
                <?php
                /**
                 * Hook: woocommerce_single_product_summary.
                 *
                 * @hooked woocommerce_template_single_title - 5
                 * @hooked woocommerce_template_single_rating - 10
                 * @hooked woocommerce_template_single_price - 10
                 * @hooked woocommerce_template_single_excerpt - 20
                 * @hooked woocommerce_template_single_add_to_cart - 30
                 * @hooked woocommerce_template_single_meta - 40
                 * @hooked woocommerce_template_single_sharing - 50
                 * @hooked WC_Structured_Data::generate_product_data() - 60
                 */
                do_action( 'woocommerce_single_product_summary' );
                ?>
            </section>

            <!-- وسط: جزئیات محصول -->
            <section class="product-details" style="padding: 0 20px;">
                <h3 style="border-bottom: 2px solid #333; display: inline-block; padding-bottom: 5px; margin-bottom: 20px;">مشخصات محصول</h3>
                <div class="product-content">
                    <?php the_content(); ?>
                </div>
            </section>

            <!-- چپ: گالری تصاویر -->
            <section class="product-gallery">
                <?php
                /**
                 * Hook: woocommerce_before_single_product_summary.
                 *
                 * @hooked woocommerce_show_product_sale_flash - 10
                 * @hooked woocommerce_show_product_images - 20
                 */
                do_action( 'woocommerce_before_single_product_summary' );
                ?>
            </section>
        </div>

        <div class="woocommerce-tabs wc-tabs-wrapper mt-5">
            <?php woocommerce_output_product_data_tabs(); ?>
        </div>

        <?php
        /**
         * Hook: woocommerce_after_single_product_summary.
         *
         * @hooked woocommerce_output_product_data_tabs - 10 (removed above and called manually for layout)
         * @hooked woocommerce_upsell_display - 15
         * @hooked woocommerce_output_related_products - 20
         */
        do_action( 'woocommerce_after_single_product_summary' );
        ?>

    <?php endwhile; // end of the loop. ?>
</main>

<?php get_footer( 'shop' ); ?>
