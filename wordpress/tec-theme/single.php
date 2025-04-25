<?php
/**
 * The template for displaying all single posts
 *
 * @package TEC_Theme
 */

get_header();
?>

<main id="primary" class="site-main">
    <div class="container">
        <?php
        while (have_posts()) : the_post();

            get_template_part('template-parts/content/content', get_post_type());

            // If comments are open or we have at least one comment, load up the comment template.
            if (comments_open() || get_comments_number()) :
                comments_template();
            endif;

            // Previous/next post navigation.
            the_post_navigation(array(
                'prev_text' => '<span class="screen-reader-text">' . __('Previous post:', 'tec-theme') . '</span> <span class="post-title">%title</span>',
                'next_text' => '<span class="screen-reader-text">' . __('Next post:', 'tec-theme') . '</span> <span class="post-title">%title</span>',
            ));

        endwhile; // End of the loop.
        ?>
    </div>
</main>

<?php get_footer(); ?>