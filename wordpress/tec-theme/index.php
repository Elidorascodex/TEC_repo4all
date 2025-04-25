<?php
/**
 * The main template file
 *
 * @package TEC_Theme
 */

get_header();
?>

<main id="primary" class="site-main">
    <div class="container">
        <?php if (is_home() && !is_front_page()) : ?>
            <header class="page-header">
                <h1 class="page-title"><?php single_post_title(); ?></h1>
            </header>
        <?php endif; ?>

        <?php if (have_posts()) : ?>
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
    
    <?php if (is_active_sidebar('sidebar-1')) : ?>
        <aside id="secondary" class="widget-area">
            <div class="container">
                <?php dynamic_sidebar('sidebar-1'); ?>
            </div>
        </aside>
    <?php endif; ?>
</main>

<?php get_footer(); ?>