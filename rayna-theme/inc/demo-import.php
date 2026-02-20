<?php
/**
 * Configuration for One Click Demo Import plugin
 */

function rayna_import_files() {
    return array(
        array(
            'import_file_name'           => 'Rayna Professional Demo',
            'categories'                 => array( 'فروشگاهی' ),
            'import_file_url'            => get_template_directory_uri() . '/demo/demo-content.xml',
            'import_widget_file_url'     => get_template_directory_uri() . '/demo/widgets.wie',
            'import_customizer_file_url' => get_template_directory_uri() . '/demo/customizer.dat',
            'import_preview_image_url'   => get_template_directory_uri() . '/screenshot.png',
            'import_notice'              => __( 'پس از وارد کردن دمو، حتماً تنظیمات پیوندهای یکتا را روی "نام نوشته" قرار دهید.', 'rayna' ),
            'preview_url'                => 'https://rayna-demo.ir',
        ),
    );
}
add_filter( 'ocdi/import_files', 'rayna_import_files' );

function rayna_after_import_setup() {
    // Assign front page and posts page (after import)
    $front_page_id = get_page_by_title( 'خانه' );
    $blog_page_id  = get_page_by_title( 'وبلاگ' );

    if ( $front_page_id && $blog_page_id ) {
        update_option( 'show_on_front', 'page' );
        update_option( 'page_on_front', $front_page_id->ID );
        update_option( 'page_for_posts', $blog_page_id->ID );
    }
}
add_action( 'ocdi/after_import', 'rayna_after_import_setup' );
