<?php get_header(); ?>

    <!-- بخش محصولات جدید (استوری) -->
    <section class="new-products">
        <div class="container">
            <div class="products-stories-container">
                <?php
                // Fetch recent products for stories
                $recent_products = array();
                if ( class_exists( 'WooCommerce' ) ) {
                    $recent_products = wc_get_products(array('limit' => 10, 'orderby' => 'date', 'order' => 'DESC'));
                }

                if ( ! empty( $recent_products ) ) :
                    foreach ( $recent_products as $product ) :
                        $image_id  = $product->get_image_id();
                        $image_url = wp_get_attachment_image_url( $image_id, 'thumbnail' );
                        ?>
                        <a href="<?php echo get_permalink( $product->get_id() ); ?>" class="product-story">
                            <div class="story-circle">
                                <img src="<?php echo $image_url ? $image_url : 'https://via.placeholder.com/100'; ?>" alt="<?php echo $product->get_name(); ?>">
                            </div>
                            <p><?php echo mb_strimwidth($product->get_name(), 0, 15, "..."); ?></p>
                        </a>
                        <?php
                    endforeach;
                else:
                    // Fallback static items if no products
                    for($i=1; $i<=5; $i++): ?>
                        <a href="#" class="product-story">
                            <div class="story-circle"><img src="https://picsum.photos/seed/story<?php echo $i; ?>/100/100.jpg" alt="محصول"></div>
                            <p>محصول <?php echo $i; ?></p>
                        </a>
                    <?php endfor;
                endif;
                ?>
            </div>
        </div>
    </section>

    <!-- بنر اصلی سایت -->
    <section class="main-banner">
        <?php if ( get_header_image() ) : ?>
            <img src="<?php header_image(); ?>" alt="بنر اصلی">
        <?php else : ?>
            <img src="https://picsum.photos/id/10/1200/400" alt="بنر اصلی">
        <?php endif; ?>
    </section>

    <!-- فروش ویژه هفتگی -->
    <section class="weekly-specials">
        <div class="container">
            <div class="specials-header">
                <div class="specials-title-container">
                    <h2>WEEKLY SPECIALS</h2>
                    <h3>فروش ویژه هفتگی</h3>
                </div>
                <a href="<?php echo class_exists( 'WooCommerce' ) ? wc_get_page_permalink( 'shop' ) : '#'; ?>" class="view-all-link">مشاهده و خرید <i class="fas fa-arrow-left"></i></a>
            </div>
            <div class="specials-grid">
                <?php
                $featured_products = array();
                if ( class_exists( 'WooCommerce' ) ) {
                    $featured_products = wc_get_products(array('limit' => 4, 'featured' => true));
                    if ( empty( $featured_products ) ) {
                        $featured_products = wc_get_products(array('limit' => 4, 'on_sale' => true));
                    }
                }

                if ( ! empty( $featured_products ) ) :
                    foreach ( $featured_products as $product ) :
                        wc_get_template( 'content-product.php', array( 'product' => $product ) );
                    endforeach;
                else:
                    echo '<p style="color:#fff; text-align:center; width:100%;">محصولی برای نمایش در این بخش وجود ندارد. محصولات ویژه یا دارای تخفیف اضافه کنید.</p>';
                endif;
                ?>
            </div>
        </div>
    </section>

    <!-- دسته بندی محصولات -->
    <section class="categories-section">
        <div class="container">
            <h2 class="section-title">دسته بندی محصولات</h2>
            <div class="categories-grid">
                <?php
                $wccategories = get_terms( 'product_cat', array( 'hide_empty' => false, 'number' => 4 ) );
                if ( ! empty( $wccategories ) ) :
                    foreach ( $wccategories as $cat ) :
                        $thumbnail_id = get_term_meta( $cat->term_id, 'thumbnail_id', true );
                        $image = wp_get_attachment_url( $thumbnail_id );
                        ?>
                        <a href="<?php echo get_term_link( $cat ); ?>" class="category-item">
                            <img src="<?php echo $image ? $image : 'https://via.placeholder.com/100'; ?>" alt="<?php echo $cat->name; ?>">
                            <p><?php echo $cat->name; ?></p>
                        </a>
                        <?php
                    endforeach;
                else:
                    ?>
                    <a href="#" class="category-item"><p>دسته‌بندی یافت نشد</p></a>
                    <?php
                endif;
                ?>
            </div>
        </div>
    </section>

    <!-- پرفروش ترین های مردانه -->
    <section class="products-section">
        <div class="container">
            <div class="section-header-wrapper">
                <div>
                    <h2 class="section-title-shadow">BEST FOR MEN</h2>
                    <h2 class="section-title">پرفروش ترین محصولات <span class="highlight-red">مردانه</span></h2>
                </div>
                <a href="#" class="view-all-link">مشاهده و خرید <i class="fas fa-arrow-left"></i></a>
            </div>
            <div class="products-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 30px;">
                <?php
                // Query for Men category products
                $men_products = array();
                if ( class_exists( 'WooCommerce' ) ) {
                    $men_products = wc_get_products(array('limit' => 4, 'category' => array('men', 'مردانه')));
                }

                if ( ! empty( $men_products ) ) :
                    foreach ( $men_products as $product ) :
                        wc_get_template( 'content-product.php', array( 'product' => $product ) );
                    endforeach;
                else:
                    echo '<p>محصولی در دسته‌بندی مردانه یافت نشد.</p>';
                endif;
                ?>
            </div>
        </div>
    </section>

<?php get_footer(); ?>
