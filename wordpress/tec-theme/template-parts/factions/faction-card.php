<?php
/**
 * Template part for displaying faction cards
 *
 * @package TEC_Theme
 */

// This template expects $faction variable to be set
if (!isset($faction) || !is_array($faction)) {
    return;
}

// Get faction properties with defaults
$name = isset($faction['name']) ? $faction['name'] : 'Unknown Faction';
$description = isset($faction['description']) ? $faction['description'] : '';
$ethos = isset($faction['ethos']) ? $faction['ethos'] : '';
$colors = isset($faction['colors']) && is_array($faction['colors']) ? $faction['colors'] : ['#000000', '#FFFFFF'];
$primary_color = $colors[0] ?? '#000000';
$secondary_color = $colors[1] ?? '#FFFFFF';
$faction_slug = sanitize_title($name);
?>

<div class="faction-card faction-<?php echo esc_attr($faction_slug); ?>" 
     style="--faction-primary: <?php echo esc_attr($primary_color); ?>; 
            --faction-secondary: <?php echo esc_attr($secondary_color); ?>;">
    
    <div class="faction-card-header">
        <div class="faction-icon"></div>
        <h3 class="faction-name"><?php echo esc_html($name); ?></h3>
    </div>
    
    <div class="faction-card-content">
        <?php if (!empty($description)) : ?>
            <p class="faction-description"><?php echo esc_html($description); ?></p>
        <?php endif; ?>
        
        <?php if (!empty($ethos)) : ?>
            <div class="faction-ethos">
                <blockquote>"<?php echo esc_html($ethos); ?>"</blockquote>
            </div>
        <?php endif; ?>
        
        <?php if (!empty($faction['associated_tokens'])) : ?>
            <div class="faction-tokens">
                <span class="tokens-label">Associated Tokens:</span>
                <div class="token-list">
                    <?php foreach ($faction['associated_tokens'] as $token) : ?>
                        <span class="token-badge"><?php echo esc_html($token); ?></span>
                    <?php endforeach; ?>
                </div>
            </div>
        <?php endif; ?>
    </div>
    
    <div class="faction-card-footer">
        <a href="<?php echo esc_url(home_url('/faction/' . $faction_slug)); ?>" class="faction-link">Learn More</a>
    </div>
</div>