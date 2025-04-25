<?php
/**
 * The template for displaying archive pages
 *
 * @package TEC_Theme
 */

get_header();
?>

<main id="primary" class="site-main">
    <div class="container">
        <?php if (have_posts()) : ?>
            <header class="page-header">
                <?php
                the_archive_title('<h1 class="page-title">', '</h1>');
                the_archive_description('<div class="archive-description">', '</div>');
                ?>
            </header><!-- .page-header -->

            <div class="tec-posts-grid">
                <?php while (have_posts()) : the_post(); ?>
                    <?php get_template_part('template-parts/content/content', get_post_type()); ?>
                <?php endwhile; ?>
            </div>

            <?php the_posts_navigation(array(
                'prev_text' => '&larr; ' . esc_html__('Older posts', 'tec-theme'),
                'next_text' => esc_html__('Newer posts', 'tec-theme') . ' &rarr;',
            )); ?>
        
        <?php else : ?>
            <?php get_template_part('template-parts/content/content', 'none'); ?>
        <?php endif; ?>
    </div>
</main>

<?php get_footer(); ?>