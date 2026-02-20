<?php get_header(); ?>

<div class="container my-5">
    <header class="page-header mb-5">
        <h1 class="page-title">
            <?php
            /* translators: %s: search query. */
            printf( esc_html__( 'نتایج جستجو برای: %s', 'rayna' ), '<span>' . get_search_query() . '</span>' );
            ?>
        </h1>
    </header>

    <?php if ( have_posts() ) : ?>
        <div class="products-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 30px;">
            <?php while ( have_posts() ) : the_post(); ?>
                <?php
                if ( 'product' === get_post_type() ) {
                    wc_get_template_part( 'content', 'product' );
                } else {
                    get_template_part( 'template-parts/content', 'search' );
                }
                ?>
            <?php endwhile; ?>
        </div>

        <div class="pagination-wrapper mt-5">
            <?php the_posts_pagination(); ?>
        </div>

    <?php else : ?>
        <p><?php _e( 'متاسفانه هیچ نتیجه‌ای برای جستجوی شما پیدا نشد.', 'rayna' ); ?></p>
        <?php get_search_form(); ?>
    <?php endif; ?>
</div>

<?php get_footer(); ?>
