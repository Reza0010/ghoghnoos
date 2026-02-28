<?php
/**
 * Template part for displaying results in search pages
 */

?>

<article id="post-<?php the_ID(); ?>" <?php post_class( 'product-card' ); ?>>
	<div class="product-info">
		<header class="entry-header">
			<?php the_title( sprintf( '<h2 class="entry-title" style="font-size:1.2rem;"><a href="%s" rel="bookmark">', esc_url( get_permalink() ) ), '</a></h2>' ); ?>
		</header>

		<div class="entry-summary">
			<?php the_excerpt(); ?>
		</div>

		<footer class="entry-footer">
			<a href="<?php echo esc_url( get_permalink() ); ?>" class="view-all-link" style="padding: 5px 15px; font-size: 0.8rem;">ادامه مطلب</a>
		</footer>
	</div>
</article>
