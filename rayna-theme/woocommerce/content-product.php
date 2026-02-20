<?php
/**
 * The template for displaying product content within loops
 */

defined( 'ABSPATH' ) || exit;

global $product;

// Ensure visibility.
if ( empty( $product ) || ! $product->is_visible() ) {
	return;
}
?>
<div <?php wc_product_class( 'product-card', $product ); ?>>
    <div class="product-image">
        <a href="<?php the_permalink(); ?>">
            <?php echo $product->get_image(); ?>
        </a>
    </div>
    <div class="product-info">
        <h4 class="product-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h4>
        <div class="price-wrapper">
            <?php echo $product->get_price_html(); ?>
        </div>
        <div class="product-actions">
            <?php woocommerce_template_loop_add_to_cart(); ?>
        </div>
    </div>
</div>
