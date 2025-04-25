<?php
/**
 * Template part for displaying full faction details
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
$primary_mission = isset($faction['primary_mission']) ? $faction['primary_mission'] : '';
$faction_slug = sanitize_title($name);
?>

<div class="faction-full faction-<?php echo esc_attr($faction_slug); ?>" 
     style="--faction-primary: <?php echo esc_attr($primary_color); ?>; 
            --faction-secondary: <?php echo esc_attr($secondary_color); ?>;">
    
    <div class="faction-header">
        <div class="faction-banner">
            <div class="faction-icon-large"></div>
            <h1 class="faction-title"><?php echo esc_html($name); ?></h1>
        </div>
        
        <?php if (isset($faction['alignment'])) : ?>
            <div class="faction-alignment">
                <span class="alignment-label">Alignment:</span>
                <span class="alignment-value"><?php echo esc_html($faction['alignment']); ?></span>
            </div>
        <?php endif; ?>
    </div>
    
    <div class="faction-content">
        <div class="faction-main">
            <?php if (!empty($description)) : ?>
                <div class="faction-section">
                    <h2 class="section-title">About</h2>
                    <div class="faction-about">
                        <p><?php echo esc_html($description); ?></p>
                    </div>
                </div>
            <?php endif; ?>
            
            <?php if (!empty($ethos)) : ?>
                <div class="faction-section">
                    <h2 class="section-title">Ethos</h2>
                    <div class="faction-ethos-full">
                        <blockquote>"<?php echo esc_html($ethos); ?>"</blockquote>
                    </div>
                </div>
            <?php endif; ?>
            
            <?php if (!empty($primary_mission)) : ?>
                <div class="faction-section">
                    <h2 class="section-title">Primary Mission</h2>
                    <p><?php echo esc_html($primary_mission); ?></p>
                </div>
            <?php endif; ?>
        </div>
        
        <div class="faction-sidebar">
            <?php if (isset($faction['leader'])) : ?>
                <div class="faction-info-box">
                    <h3>Leadership</h3>
                    <div class="leader-info">
                        <div class="leader-name"><?php echo esc_html($faction['leader']['name']); ?></div>
                        <?php if (isset($faction['leader']['title'])) : ?>
                            <div class="leader-title"><?php echo esc_html($faction['leader']['title']); ?></div>
                        <?php endif; ?>
                        
                        <?php if (isset($faction['leader']['elected'])) : ?>
                            <div class="leader-elected">
                                <?php echo $faction['leader']['elected'] ? 'Democratically Elected' : 'Appointed Position'; ?>
                            </div>
                        <?php endif; ?>
                    </div>
                </div>
            <?php endif; ?>
            
            <?php if (isset($faction['membership']) && is_array($faction['membership'])) : ?>
                <div class="faction-info-box">
                    <h3>Membership</h3>
                    <ul class="membership-details">
                        <?php if (isset($faction['membership']['open'])) : ?>
                            <li>
                                <span class="detail-label">Membership Status:</span>
                                <span class="detail-value"><?php echo $faction['membership']['open'] ? 'Open' : 'Closed'; ?></span>
                            </li>
                        <?php endif; ?>
                        
                        <?php if (isset($faction['membership']['limited_time'])) : ?>
                            <li>
                                <span class="detail-label">Limited Enrollment:</span>
                                <span class="detail-value"><?php echo $faction['membership']['limited_time'] ? 'Yes' : 'No'; ?></span>
                            </li>
                        <?php endif; ?>
                        
                        <?php if (isset($faction['membership']['join_requirements'])) : ?>
                            <li>
                                <span class="detail-label">Requirements:</span>
                                <span class="detail-value"><?php echo esc_html($faction['membership']['join_requirements']); ?></span>
                            </li>
                        <?php endif; ?>
                    </ul>
                </div>
            <?php endif; ?>
            
            <?php if (!empty($faction['associated_tokens'])) : ?>
                <div class="faction-info-box">
                    <h3>Associated Tokens</h3>
                    <div class="token-list-full">
                        <?php foreach ($faction['associated_tokens'] as $token) : ?>
                            <div class="token-item">
                                <span class="token-badge"><?php echo esc_html($token); ?></span>
                                <a href="<?php echo esc_url(home_url('/crypto/' . strtolower($token))); ?>" class="token-link">View Token</a>
                            </div>
                        <?php endforeach; ?>
                    </div>
                </div>
            <?php endif; ?>
            
            <?php if (!empty($faction['perks']) && is_array($faction['perks'])) : ?>
                <div class="faction-info-box">
                    <h3>Faction Perks</h3>
                    <ul class="faction-perks">
                        <?php foreach ($faction['perks'] as $perk) : ?>
                            <li><?php echo esc_html($perk); ?></li>
                        <?php endforeach; ?>
                    </ul>
                </div>
            <?php endif; ?>
        </div>
    </div>
    
    <?php if (isset($faction['forbidden']) && $faction['forbidden']) : ?>
        <div class="faction-forbidden-notice">
            <span class="forbidden-icon">⚠</span>
            <span class="forbidden-text">This faction cannot be joined by players</span>
        </div>
    <?php else : ?>
        <div class="faction-cta">
            <a href="<?php echo esc_url(home_url('/join-faction/' . $faction_slug)); ?>" class="btn btn-faction">Join <?php echo esc_html($name); ?></a>
        </div>
    <?php endif; ?>
</div>