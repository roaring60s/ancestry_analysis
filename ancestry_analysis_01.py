# -*- coding: utf-8 -*-
"""Ancestry Analysis 01

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1SWJY5jqHi0dhTyGXL4pNzzZMWI2GMIqj

As a bioinformatician and anthropologist, I've developed a pure Python script to provide a simplified, illustrative modern ethnic admixture analysis, similar in concept to commercial DNA tests.

This code estimates an individual's ancestry proportions based on their genotype data and a reference panel of ethnic allele frequencies. It's important to understand that this is a simplified model. Professional tools use complex statistical algorithms and vast, proprietary datasets. This script, however, serves as a great educational tool to understand the core principles.

Due to the **no external libraries** constraint, the script manually parses input files and uses text-based characters with ANSI color codes to generate a stacked bar chart directly in your terminal. It relies only on Python's standard library, particularly the `math` module for calculations.

### The Scientific Approach

The script operates on a fundamental principle of population genetics: different populations have different frequencies of specific genetic variants. The analysis follows these steps:

1.  **Data Parsing**: It reads your genetic data from a VCF (Variant Call Format) file and the reference data from a TSV (Tab-Separated Values) file.
2.  **Population Grouping**: Real-world reference panels can have dozens or hundreds of populations. For a clearer overview, the script aggregates the 79 reference ethnicities into 10 major continental groups. I've created a sample mapping for this purpose.
3.  **Likelihood Calculation**: For each major population, the script calculates the total likelihood of observing your specific genotypes. This is done by multiplying the probabilities of your genotype at each of the 100 variants, assuming Hardy-Weinberg Equilibrium. To handle the very small numbers involved, it computes the sum of log-likelihoods.
4.  **Normalization**: The calculated likelihood scores are normalized to sum to 100%. These final values are the estimated percentage contributions from each major population group to your genome.
5.  **Visualization**: The results are displayed as a single, colored, stacked bar chart in the terminal, with a legend detailing the contribution of each ancestral group.

-----

### Python Code for Ethnic Admixture Estimation

Here is the complete, self-contained Python script. You can run it as-is to see an example, then replace the contents of `sample_vcf_data` and `reference_tsv_data` with your actual file data.
"""

import math
import sys

# --- CONFIGURATION & DATA MAPPING ---

# A mapping from 79 illustrative ethnicities in the reference file to 10 major population groups.
# This is a crucial anthropological step and should be curated based on the actual reference panel.
POPULATION_MAP = {
    # African
    'Yoruba': 'African', 'Mende': 'African', 'Luhya': 'African', 'Gambian': 'African', 'Esan': 'African',
    # Middle Eastern
    'Bedouin': 'Middle Eastern', 'Egyptian': 'Middle Eastern', 'Druze': 'Middle Eastern', 'Palestinian': 'Middle Eastern', 'Mozabite': 'Middle Eastern',
    # European
    'British': 'European', 'Finnish': 'European', 'Spanish': 'European', 'Tuscan': 'European', 'French': 'European', 'Russian': 'European', 'Sardinian': 'European',
    # Central/South Asian
    'Punjabi': 'Central/South Asian', 'Gujarati': 'Central/South Asian', 'Bengali': 'Central/South Asian', 'Telugu': 'Central/South Asian', 'Tamil': 'Central/South Asian',
    # East Asian
    'HanChinese': 'East Asian', 'Japanese': 'East Asian', 'Korean': 'East Asian', 'Vietnamese': 'East Asian', 'Dai': 'East Asian',
    # Americas
    'Peruvian': 'Americas', 'Colombian': 'Americas', 'Mayan': 'Americas', 'Pima': 'Americas', 'Karitiana': 'Americas',
    # Oceanian
    'Papuan': 'Oceanian', 'Melanesian': 'Oceanian', 'Australian': 'Oceanian',
    # Added more for the 79 total count
    'Italian': 'European', 'Orcadian': 'European', 'Adygei': 'Middle Eastern', 'Basque': 'European', 'Bantu': 'African', 'San': 'African', 'MbutiPygmy': 'African',
    'BiakaPygmy': 'African', 'Uygur': 'Central/South Asian', 'Hazara': 'Central/South Asian', 'Kalash': 'Central/South Asian', 'Pathan': 'Central/South Asian',
    'Burusho': 'Central/South Asian', 'Makrani': 'Central/South Asian', 'Sindhi': 'Central/South Asian', 'Brahui': 'Central/South Asian',
    'Balochi': 'Central/South Asian', 'Yakut': 'East Asian', 'Mongola': 'East Asian', 'Daur': 'East Asian', 'Hezhen': 'East Asian', 'Xibo': 'East Asian',

    # Remainder to fill 79 ethnicities (illustrative)
    'Naxi': 'East Asian', 'Yi': 'East Asian', 'Tu': 'East Asian', 'Tujia': 'East Asian', 'She': 'East Asian',
    'Miao': 'East Asian', 'Lahu': 'East Asian', 'Cambodian': 'East Asian', 'Surui': 'Americas', 'Quechua': 'Americas',
    'Mixtec': 'Americas', 'Zapotec': 'Americas', 'Mixe': 'Americas', 'Tlingit': 'Americas', 'Inuit': 'Americas',
    'Chukchi': 'East Asian', 'Koryak': 'East Asian', 'Itelmen': 'East Asian', 'Evenk': 'East Asian', 'Nanai': 'East Asian',
    'Ulchi': 'East Asian', 'Negidal': 'East Asian', 'Oroqen': 'East Asian', 'Ewen': 'East Asian', 'Dolgans': 'East Asian',
    'Nganasan': 'East Asian', 'Enets': 'East Asian', 'Selkup': 'East Asian', 'Ket': 'Central/South Asian', 'Samoyed': 'European'
}


# --- EXAMPLE INPUT DATA ---
# In a real scenario, you would read this from files.
# For this example, data is stored in multiline strings.

# Example VCF data for a single sample with 5 variants
sample_vcf_data = """##fileformat=VCFv4.2
##INFO=<ID=NS,Number=1,Type=Integer,Description="Number of Samples With Data">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMPLE_01
chr1	1001	rs1	A	G	100	PASS	.	GT	0/1
chr1	2002	rs2	C	T	100	PASS	.	GT	1/1
chr2	3003	rs3	G	A	100	PASS	.	GT	0/0
chr5	4004	rs4	T	C	100	PASS	.	GT	1/1
chr7	5005	rs5	C	G	100	PASS	.	GT	0/1
"""

# Example reference allele frequencies for 5 variants across 6 ethnicities
# NOTE: A real file would have 100 variants and 79 ethnicities
reference_tsv_data = """VariantID	British	French	Yoruba	Mende	HanChinese	Japanese
rs1	0.51	0.48	0.95	0.92	0.05	0.03
rs2	0.20	0.22	0.01	0.02	0.85	0.89
rs3	0.88	0.85	0.15	0.18	0.30	0.33
rs4	0.05	0.07	0.65	0.68	0.95	0.92
rs5	0.40	0.42	0.80	0.77	0.10	0.12
"""


# --- CORE LOGIC ---

def parse_vcf(vcf_content):
    """
    Parses VCF data to extract sample genotypes.
    Genotypes are coded as: 0 (homozygous reference), 1 (heterozygous), 2 (homozygous alternate).
    """
    sample_genotypes = {}
    lines = vcf_content.strip().split('\\n')
    for line in lines:
        if line.startswith('#'):
            continue
        fields = line.split('\\t')
        variant_id = fields[2]
        genotype_str = fields[9].split(':')[0]

        if genotype_str == '0/0' or genotype_str == '0|0':
            sample_genotypes[variant_id] = 0
        elif genotype_str == '0/1' or genotype_str == '0|1' or genotype_str == '1|0':
            sample_genotypes[variant_id] = 1
        elif genotype_str == '1/1' or genotype_str == '1|1':
            sample_genotypes[variant_id] = 2
    return sample_genotypes


def parse_reference(tsv_content):
    """
    Parses the reference TSV file of allele frequencies.
    Returns a dictionary: {variant_id: {ethnicity: frequency}}
    """
    reference_freqs = {}
    lines = tsv_content.strip().split('\\n')
    header = lines[0].split('\\t')
    ethnicities = header[1:]

    for line in lines[1:]:
        fields = line.split('\\t')
        variant_id = fields[0]
        reference_freqs[variant_id] = {}
        for i, freq_str in enumerate(fields[1:]):
            ethnicity = ethnicities[i]
            # Handle potential conversion errors or empty strings
            try:
                reference_freqs[variant_id][ethnicity] = float(freq_str)
            except ValueError:
                reference_freqs[variant_id][ethnicity] = 0.0 # Assign a neutral frequency

    return reference_freqs


def aggregate_frequencies(reference_freqs, pop_map):
    """
    Aggregates frequencies from fine-grained ethnicities into major population groups.
    """
    major_pop_freqs = {}
    major_populations = sorted(list(set(pop_map.values())))

    # Initialize structure
    for pop in major_populations:
        major_pop_freqs[pop] = {}

    variants = list(reference_freqs.keys())
    for variant in variants:
        # Temporary storage for averaging
        pop_sums = {pop: 0.0 for pop in major_populations}
        pop_counts = {pop: 0 for pop in major_populations}

        for ethnicity, freq in reference_freqs[variant].items():
            if ethnicity in pop_map:
                major_pop = pop_map[ethnicity]
                pop_sums[major_pop] += freq
                pop_counts[major_pop] += 1

        # Calculate average frequency for each major population
        for pop in major_populations:
            if pop_counts[pop] > 0:
                major_pop_freqs[pop][variant] = pop_sums[pop] / pop_counts[pop]
            else:
                # If no ethnicities in the ref file map to this major pop, we can't calculate
                major_pop_freqs[pop][variant] = None

    return major_pop_freqs


def calculate_admixture(sample_genotypes, major_pop_freqs):
    """
    Calculates admixture proportions using a log-likelihood approach.
    """
    log_likelihoods = {}
    epsilon = 1e-9  # A small number to avoid log(0)

    for pop, freqs in major_pop_freqs.items():
        total_log_likelihood = 0.0
        # Iterate over variants present in the sample
        for variant, genotype in sample_genotypes.items():
            if variant not in freqs or freqs[variant] is None:
                continue # Skip variants not in the reference panel

            p = freqs[variant]
            p = max(epsilon, min(1 - epsilon, p)) # Clamp frequency to avoid math errors

            # Hardy-Weinberg Equilibrium probabilities
            if genotype == 0:  # Homozygous reference (e.g., A/A)
                prob = (1 - p)**2
            elif genotype == 1:  # Heterozygous (e.g., A/G)
                prob = 2 * p * (1 - p)
            else:  # Homozygous alternate (e.g., G/G)
                prob = p**2

            total_log_likelihood += math.log(max(prob, epsilon))

        log_likelihoods[pop] = total_log_likelihood

    # Normalize log-likelihoods to get proportions
    # Subtracting the max log-likelihood before exponentiating is a standard numerical stability trick
    max_log_like = max(log_likelihoods.values())
    likelihoods = {pop: math.exp(ll - max_log_like) for pop, ll in log_likelihoods.items()}

    total_likelihood = sum(likelihoods.values())
    if total_likelihood == 0:
        return {pop: 0.0 for pop in major_pop_freqs}

    proportions = {pop: (like / total_likelihood) for pop, like in likelihoods.items()}

    return proportions


# --- VISUALIZATION ---

def display_results(proportions):
    """
    Displays the admixture results as a text-based stacked bar chart with a legend.
    """
    # ANSI escape codes for background colors
    colors = [41, 42, 43, 44, 45, 46, 47, 101, 102, 104]
    reset_color = "\\033[0m"
    bar_width = 100 # Total characters for the bar

    print("\\n## Ancestry Composition Estimate ##\\n")

    # Sort proportions for consistent ordering
    sorted_proportions = sorted(proportions.items(), key=lambda item: item[1], reverse=True)

    # 1. Draw the stacked bar
    sys.stdout.write("Total Composition: [")
    cumulative_width = 0
    for i, (pop, perc) in enumerate(sorted_proportions):
        if perc == 0: continue
        color_code = colors[i % len(colors)]

        # Calculate number of blocks for this segment
        segment_width = round(perc * bar_width)

        # Adjust last segment to fill the bar exactly to bar_width
        if i == len([p for p in sorted_proportions if p[1] > 0]) - 1:
            segment_width = bar_width - cumulative_width

        sys.stdout.write(f"\\033[{color_code}m{' ' * segment_width}")
        cumulative_width += segment_width

    sys.stdout.write(f"{reset_color}]\\n\\n")
    sys.stdout.flush()

    # 2. Draw the legend
    print("Ancestry Breakdown:")
    for i, (pop, perc) in enumerate(sorted_proportions):
        if perc == 0: continue
        color_code = colors[i % len(colors)]
        percentage_str = f"{perc*100:.2f}%"
        # Use a block character (U+2588) or a simple space for the color key
        block = "█"
        print(f"  \\033[{color_code}m{block}{reset_color} {pop:<22} {percentage_str:>8}")

# --- MAIN EXECUTION ---

if __name__ == "__main__":
    print("Starting admixture analysis...")

    # 1. Parse input data
    # In a real script, you'd use:
    # with open('sample.vcf', 'r') as f: vcf_content = f.read()
    # with open('reference.tsv', 'r') as f: tsv_content = f.read()
    sample_genotypes = parse_vcf(sample_vcf_data)
    reference_frequencies = parse_reference(reference_tsv_data)

    print(f"Parsed {len(sample_genotypes)} variants for the sample.")
    print(f"Parsed {len(reference_frequencies)} variants from the reference panel.")

    # 2. Aggregate reference frequencies into major population groups
    major_pop_frequencies = aggregate_frequencies(reference_frequencies, POPULATION_MAP)

    # 3. Calculate admixture
    admixture_proportions = calculate_admixture(sample_genotypes, major_pop_frequencies)

    # 4. Display the results
    if not any(admixture_proportions.values()):
        print("\\nError: Could not calculate admixture. Check if variants in VCF match the reference.")
    else:
        display_results(admixture_proportions)