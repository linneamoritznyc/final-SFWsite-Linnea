<?php
/**
 * Plugin Name: SFW Publications
 * Description: The Soil Food Web Foundation publications list with summaries, search and filters. Put [sfw_publications] on the Publications page. The list is read from data/sfw-publications-final.csv inside this plugin: replace that file to update it.
 * Version: 1.0.0
 * Author: Soil Food Web Foundation
 * License: GPL-2.0-or-later
 * Text Domain: sfw-publications
 */

if (!defined('ABSPATH')) {
    exit;
}

define('SFWP_VERSION', '1.0.0');
define('SFWP_CSV', __DIR__ . '/data/sfw-publications-final.csv');

/** CSV collection value => [slug, label readers see]. Order is the page order. */
function sfwp_collections() {
    return array(
        "Dr. Elaine's publications"   => array('elaine', 'Dr. Elaine’s publications'),
        'Other relevant publications' => array('field', 'Soil food web science'),
        'Internet articles'           => array('internet', 'Internet articles'),
    );
}

/** Topic facets: name, what it is about, [tag => definition]. */
function sfwp_facets() {
    return array(
        array('Organisms', 'The groups Soil Food Web students learn to identify under the microscope.', array(
            'bacteria' => 'Studies that measure, count or manipulate soil or compost bacteria.',
            'fungi' => 'Studies of soil fungi, fungal hyphae or fungal biomass, including fungal plant pathogens.',
            'mycorrhizal fungi' => 'Fungi that live in partnership with plant roots (arbuscular and ectomycorrhizal).',
            'protozoa' => 'Flagellates, amoebae and ciliates, the main grazers of bacteria.',
            'nematodes' => 'Beneficial and root-feeding nematodes.',
            'soil arthropods' => 'Mites, springtails, symphylans and other small soil animals.',
            'earthworms' => 'Earthworms, including the worms used to make vermicompost.',
        )),
        array('Practices and inputs', 'What a grower or land manager actually does.', array(
            'compost' => 'Making, testing or applying thermal compost.',
            'compost tea and extracts' => 'Brewed compost tea and water extracts of compost or vermicompost, used as a drench or foliar spray.',
            'vermicompost' => 'Worm castings and vermicompost as an input.',
            'cover crops and tillage' => 'Cover crops, no-till, reduced tillage, crop rotation and alley cropping.',
            'pesticides and fumigants' => 'The effects of biocides, fungicides, antibiotics and soil fumigants on soil life.',
            'engineered microbes' => 'Genetically engineered organisms released into soil, and their regulation.',
        )),
        array('Outcomes', 'The results readers care about.', array(
            'nutrient cycling' => 'Nitrogen, phosphorus and sulfur cycling, mineralization and nitrogen fixation.',
            'soil carbon' => 'Carbon storage, carbon sequestration and soil CO2 flux.',
            'decomposition' => 'Breakdown of litter, logs and other organic matter.',
            'disease suppression' => 'Biological control of plant diseases, including induced plant resistance.',
            'pest suppression' => 'Biological control of insect and other plant pests.',
            'plant growth and yield' => 'Measured plant growth, seedling vigour or crop yield.',
            'food quality' => 'Nutritional quality of crops, milk and other food.',
            'remediation' => 'Cleaning up contaminated soil or water, including heavy metals and hazardous waste sites.',
        )),
        array('Systems', 'The kind of land the study was done on.', array(
            'farms and crops' => 'Field crops, vegetables, orchards and dairy farms.',
            'horticulture and nurseries' => 'Container growing, greenhouses, nurseries, turf and ornamentals.',
            'forests' => 'Conifer, deciduous and riparian forests, and forest restoration.',
            'grasslands and rangelands' => 'Prairie, meadow and rangeland.',
            'wetlands and streams' => 'Wetlands and stream-side soils.',
            'cold and winter soils' => 'Soil life under snow and in the non-growing season.',
        )),
        array('Approach', 'The kind of work.', array(
            'soil food web' => 'Studies of the food web as a whole: who eats whom and what that does for plants.',
            'lab methods and microscopy' => 'Methods for counting, staining and measuring soil organisms.',
            'soil biodiversity' => 'The diversity of soil organisms and why it matters.',
            'policy and soil security' => 'Regulation, policy and soil as a matter of public concern.',
            'review' => 'Papers that review or summarize a body of research.',
        )),
    );
}

function sfwp_study_types() {
    return array(
        'Field study' => 'Done outdoors on real farms, forests or rangeland.',
        'Greenhouse or pot trial' => 'Plants grown in pots or containers under controlled conditions.',
        'Lab study' => 'Done in the lab, in petri dishes, microcosms or cultures.',
        'Review' => 'Summarizes earlier research.',
        'Method' => 'Describes or tests a way to measure something.',
        'Report or guide' => 'Technical reports, manuals and handbooks.',
        'Article or commentary' => 'Magazine columns, newsletters, opinion pieces and internet articles.',
    );
}

function sfwp_regions() {
    return array('North America', 'South America', 'Europe', 'Africa', 'Asia', 'Global');
}

function sfwp_slug($text) {
    return trim(preg_replace('/[^a-z0-9]+/', '-', strtolower($text)), '-');
}

/** Read the CSV (UTF-8 with or without a BOM). Returns the rows as arrays keyed by column. */
function sfwp_read_csv($path) {
    $rows = array();
    if (!is_readable($path)) {
        return $rows;
    }
    $fh = fopen($path, 'r');
    $head = fgetcsv($fh, 0, ',', '"', '');
    if (!$head) {
        fclose($fh);
        return $rows;
    }
    $head[0] = preg_replace('/^\xEF\xBB\xBF/', '', $head[0]);
    $head = array_map('trim', $head);
    while (($r = fgetcsv($fh, 0, ',', '"', '')) !== false) {
        if (count($r) === 1 && trim($r[0]) === '') {
            continue;
        }
        $r = array_pad($r, count($head), '');
        $rows[] = array_map('trim', array_combine($head, array_slice($r, 0, count($head))));
    }
    fclose($fh);
    return $rows;
}

/** Rows -> entries, sorted oldest first inside each collection. */
function sfwp_entries() {
    $cols = sfwp_collections();
    $order = array_keys($cols);
    $out = array();
    foreach (sfwp_read_csv(SFWP_CSV) as $i => $r) {
        if (isset($r['status']) && $r['status'] !== '' && $r['status'] !== 'publish') {
            continue;
        }
        $c = isset($cols[$r['collection']]) ? $r['collection'] : 'Other relevant publications';
        $topics = array_values(array_filter(array_map('trim', explode(',', $r['topics']))));
        $out[] = array(
            'i'          => $i,
            'title'      => $r['title'],
            'year'       => (int) $r['year'],
            'type'       => $r['type'] === 'USDA' ? 'USDA publication' : $r['type'],
            'collection' => $c,
            'authors'    => $r['authors'],
            'citation'   => $r['citation'],
            'summary'    => $r['summary'],
            'useful_for' => $r['useful_for'],
            'url'        => $r['external_url'],
            'topics'     => $topics,
            'study_type' => $r['study_type'],
            'region'     => $r['region'],
        );
    }
    usort($out, function ($a, $b) use ($order) {
        $ca = array_search($a['collection'], $order);
        $cb = array_search($b['collection'], $order);
        if ($ca !== $cb) {
            return $ca - $cb;
        }
        if ($a['year'] !== $b['year']) {
            return $a['year'] - $b['year'];
        }
        return $a['i'] - $b['i'];
    });
    return $out;
}

/** What the link under the entry says: Google Scholar, DOI or Publisher page. */
function sfwp_link_label($url) {
    if (strpos($url, 'scholar.google') !== false) {
        return 'Google Scholar';
    }
    if (strpos($url, 'doi.org/') !== false) {
        return 'DOI';
    }
    return 'Publisher page';
}

function sfwp_options($values, $counts, $labels = null) {
    $html = '';
    foreach ($values as $v) {
        if (empty($counts[$v])) {
            continue;   // only values that occur
        }
        $html .= sprintf('<option value="%s">%s (%d)</option>', esc_attr(sfwp_slug($v)), esc_html($labels ? $labels[$v] : $v), $counts[$v]);
    }
    return $html;
}

function sfwp_render() {
    $entries = sfwp_entries();
    if (!$entries) {
        return '<p>The publications list could not be read.</p>';
    }
    $cols = sfwp_collections();
    $c_count = $t_count = $s_count = $r_count = array();
    foreach ($entries as $e) {
        $c_count[$e['collection']] = (isset($c_count[$e['collection']]) ? $c_count[$e['collection']] : 0) + 1;
        $s_count[$e['study_type']] = (isset($s_count[$e['study_type']]) ? $s_count[$e['study_type']] : 0) + 1;
        $r_count[$e['region']] = (isset($r_count[$e['region']]) ? $r_count[$e['region']] : 0) + 1;
        foreach ($e['topics'] as $t) {
            $t_count[$t] = (isset($t_count[$t]) ? $t_count[$t] : 0) + 1;
        }
    }
    $total = count($entries);
    $linked = count(array_filter($entries, function ($e) { return $e['url'] !== ''; }));

    ob_start();
    ?>
<div class="sfwp" id="all">
  <p class="sfwp-counts"><?php printf(
      '%d publications. %d link to the publisher record, Google Scholar or a repository copy; %d %s listed by citation because no copy was found online.',
      $total, $linked, $total - $linked, ($total - $linked) === 1 ? 'is' : 'are'); ?></p>

  <div class="sfwp-controls" data-sfwp-controls hidden>
    <ul class="sfwp-chips" aria-label="Collections">
      <li><button class="sfwp-chip" type="button" data-sfwp-chip="" aria-pressed="true">All (<?php echo (int) $total; ?>)</button></li>
      <?php foreach ($cols as $csv => $c) : if (empty($c_count[$csv])) { continue; } ?>
      <li><button class="sfwp-chip" type="button" data-sfwp-chip="<?php echo esc_attr($c[0]); ?>" aria-pressed="false"><?php echo esc_html($c[1]); ?> (<?php echo (int) $c_count[$csv]; ?>)</button></li>
      <?php endforeach; ?>
    </ul>
    <form class="sfwp-searchbar" role="search" aria-label="Filter publications" data-sfwp-form>
      <div class="sfwp-field sfwp-field--q">
        <label for="sfwp-q">Search by title, author, topic or year</label>
        <input id="sfwp-q" name="q" type="search" autocomplete="off">
      </div>
      <div class="sfwp-field">
        <label for="sfwp-topic">Topic</label>
        <select id="sfwp-topic" name="topic"><option value="">Any</option>
          <?php foreach (sfwp_facets() as $f) :
              $opts = sfwp_options(array_keys($f[2]), $t_count);
              if ($opts) { printf('<optgroup label="%s">%s</optgroup>', esc_attr($f[0]), $opts); }
          endforeach; ?>
        </select>
      </div>
      <div class="sfwp-field">
        <label for="sfwp-study">Study type</label>
        <select id="sfwp-study" name="study"><option value="">Any</option><?php echo sfwp_options(array_keys(sfwp_study_types()), $s_count); ?></select>
      </div>
      <div class="sfwp-field">
        <label for="sfwp-region">Region</label>
        <select id="sfwp-region" name="region"><option value="">Any</option><?php echo sfwp_options(sfwp_regions(), $r_count); ?></select>
      </div>
      <div class="sfwp-field">
        <label for="sfwp-sort">Sort</label>
        <select id="sfwp-sort" name="sort"><option value="">Oldest first</option><option value="newest">Newest first</option></select>
      </div>
    </form>
    <details class="sfwp-guide">
      <summary>How the tags work</summary>
      <div>
        <p>A paper gets every tag that describes its main subject, usually 2 to 5.</p>
        <?php foreach (sfwp_facets() as $f) : ?>
        <h4><?php echo esc_html($f[0]); ?></h4>
        <p class="sfwp-guide__about"><?php echo esc_html($f[1]); ?></p>
        <dl><?php foreach ($f[2] as $tag => $def) { printf('<dt>%s</dt><dd>%s</dd>', esc_html($tag), esc_html($def)); } ?></dl>
        <?php endforeach; ?>
        <h4>Study type</h4>
        <p class="sfwp-guide__about">One per paper.</p>
        <dl><?php foreach (sfwp_study_types() as $tag => $def) { printf('<dt>%s</dt><dd>%s</dd>', esc_html($tag), esc_html($def)); } ?></dl>
        <h4>Region</h4>
        <p class="sfwp-guide__about">One per paper.</p>
        <p><?php echo esc_html(implode(', ', sfwp_regions())); ?>. Region is where the study was done. Global means a review, a multi-country study, or work that is about no particular place.</p>
      </div>
    </details>
    <div class="sfwp-status">
      <p class="sfwp-count" aria-live="polite" data-sfwp-status></p>
      <button class="sfwp-clear" type="button" data-sfwp-clear hidden>Clear filters</button>
    </div>
  </div>

  <div data-sfwp-list>
    <?php foreach ($cols as $csv => $c) :
        $group = array_filter($entries, function ($e) use ($csv) { return $e['collection'] === $csv; });
        if (!$group) { continue; } ?>
    <section class="sfwp-group" data-sfwp-group="<?php echo esc_attr($c[0]); ?>">
      <h3><?php echo esc_html($c[1]); ?></h3>
      <ul class="sfwp-entries">
        <?php foreach ($group as $e) :
            $n = array_search($e, $entries, true);
            $line = implode(' · ', array_filter(array($e['authors'], $e['citation'])));
            $title = esc_html($e['title']);
            if ($e['url'] !== '') {
                $title = sprintf('<a href="%s" rel="noopener">%s</a>', esc_url($e['url']), $title);
            } ?>
        <li class="sfwp-entry" data-i="<?php echo (int) $n; ?>" data-year="<?php echo (int) $e['year']; ?>"
            data-collection="<?php echo esc_attr($c[0]); ?>"
            data-topic="<?php echo esc_attr(implode(' ', array_map('sfwp_slug', $e['topics']))); ?>"
            data-study="<?php echo esc_attr(sfwp_slug($e['study_type'])); ?>"
            data-region="<?php echo esc_attr(sfwp_slug($e['region'])); ?>"
            data-topics-text="<?php echo esc_attr(implode(' ', $e['topics'])); ?>">
          <span class="sfwp-entry__year"><?php echo (int) $e['year']; ?></span>
          <div>
            <p class="sfwp-entry__title"><?php echo $title; ?></p>
            <?php if ($line) : ?><p class="sfwp-entry__line"><?php echo esc_html($line); ?></p><?php endif; ?>
            <p class="sfwp-entry__why"><b>Summary:</b> <span data-s><?php echo esc_html($e['summary']); ?></span></p>
            <p class="sfwp-entry__why"><b>Useful for:</b> <span data-s><?php echo esc_html($e['useful_for']); ?></span></p>
            <?php if ($e['url'] !== '') : ?>
            <p class="sfwp-entry__links"><a href="<?php echo esc_url($e['url']); ?>" rel="noopener"><?php echo esc_html(sfwp_link_label($e['url'])); ?></a></p>
            <?php else : ?>
            <p class="sfwp-entry__links sfwp-entry__nolink">No online copy found. Listed by citation.</p>
            <?php endif; ?>
          </div>
          <span class="sfwp-entry__kind"><?php echo esc_html($e['type']); ?><br><?php echo esc_html($e['study_type']); ?> · <?php echo esc_html($e['region']); ?></span>
        </li>
        <?php endforeach; ?>
      </ul>
    </section>
    <?php endforeach; ?>
    <ul class="sfwp-entries" data-sfwp-flat hidden></ul>
    <div class="sfwp-empty" data-sfwp-empty hidden>
      <p>No publications match these filters.</p>
      <p><button class="sfwp-clear" type="button" data-sfwp-clear>Clear filters</button></p>
    </div>
  </div>
</div>
    <?php
    return ob_get_clean();
}

/** [sfw_publications]: the list, cached until the CSV or the plugin changes. */
function sfwp_shortcode() {
    wp_enqueue_style('sfw-publications', plugins_url('assets/sfw-publications.css', __FILE__), array(), SFWP_VERSION);
    wp_enqueue_script('sfw-publications', plugins_url('assets/sfw-publications.js', __FILE__), array(), SFWP_VERSION, true);
    $key = 'sfwp_' . md5(SFWP_VERSION . '|' . (is_readable(SFWP_CSV) ? filemtime(SFWP_CSV) . filesize(SFWP_CSV) : 'none'));
    $html = get_transient($key);
    if ($html === false) {
        $html = sfwp_render();
        set_transient($key, $html, WEEK_IN_SECONDS);
    }
    return $html;
}
add_shortcode('sfw_publications', 'sfwp_shortcode');
