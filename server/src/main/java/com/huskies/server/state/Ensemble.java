package com.huskies.server.state;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import org.springframework.data.mongodb.core.mapping.Document;

import java.util.List;
import java.util.Map;

@Document("states")
@JsonIgnoreProperties(ignoreUnknown = true)
public class Ensemble {

    @JsonProperty("schema_version")
    private String schemaVersion;
    private Meta meta;
    private Summary summary;
    private Metrics metrics;

    public String getSchemaVersion() { return schemaVersion; }
    public void setSchemaVersion(String schemaVersion) { this.schemaVersion = schemaVersion; }
    public Meta getMeta() { return meta; }
    public void setMeta(Meta meta) { this.meta = meta; }
    public Summary getSummary() { return summary; }
    public void setSummary(Summary summary) { this.summary = summary; }
    public Metrics getMetrics() { return metrics; }
    public void setMetrics(Metrics metrics) { this.metrics = metrics; }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Meta {
        private String state;
        private String plan;
        private EnsembleMeta ensemble;
        public String getState() { return state; }
        public void setState(String state) { this.state = state; }
        public String getPlan() { return plan; }
        public void setPlan(String plan) { this.plan = plan; }
        public EnsembleMeta getEnsemble() { return ensemble; }
        public void setEnsemble(EnsembleMeta ensemble) { this.ensemble = ensemble; }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class EnsembleMeta {
        private int size;
        private String method;
        private String generated;
        public int getSize() { return size; }
        public void setSize(int size) { this.size = size; }
        public String getMethod() { return method; }
        public void setMethod(String method) { this.method = method; }
        public String getGenerated() { return generated; }
        public void setGenerated(String generated) { this.generated = generated; }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Summary {
        @JsonProperty("num_plans") private int numPlans;
        @JsonProperty("num_incumbents") private int numIncumbents;
        @JsonProperty("avg_incumbent_winners") private double avgIncumbentWinners;
        @JsonProperty("avg_geo_var") private double avgGeoVar;
        @JsonProperty("avg_pop_var") private double avgPopVar;
        public int getNumPlans() { return numPlans; }
        public void setNumPlans(int v) { this.numPlans = v; }
        public int getNumIncumbents() { return numIncumbents; }
        public void setNumIncumbents(int v) { this.numIncumbents = v; }
        public double getAvgIncumbentWinners() { return avgIncumbentWinners; }
        public void setAvgIncumbentWinners(double v) { this.avgIncumbentWinners = v; }
        public double getAvgGeoVar() { return avgGeoVar; }
        public void setAvgGeoVar(double v) { this.avgGeoVar = v; }
        public double getAvgPopVar() { return avgPopVar; }
        public void setAvgPopVar(double v) { this.avgPopVar = v; }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Metrics {
        @JsonProperty("by_incumbent") private List<IncumbentMetrics> byIncumbent;
        public List<IncumbentMetrics> getByIncumbent() { return byIncumbent; }
        public void setByIncumbent(List<IncumbentMetrics> v) { this.byIncumbent = v; }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class IncumbentMetrics {
        private String id;
        private String name;
        private List<Metric> metrics;
        public String getId() { return id; }
        public void setId(String id) { this.id = id; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public List<Metric> getMetrics() { return metrics; }
        public void setMetrics(List<Metric> v) { this.metrics = v; }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Metric {
        private String id;
        private String label;
        private String unit;
        private double observed;
        @JsonProperty("observed_percentile") private double observedPercentile;
        private Distribution ensemble;
        public String getId() { return id; }
        public void setId(String id) { this.id = id; }
        public String getLabel() { return label; }
        public void setLabel(String label) { this.label = label; }
        public String getUnit() { return unit; }
        public void setUnit(String unit) { this.unit = unit; }
        public double getObserved() { return observed; }
        public void setObserved(double v) { this.observed = v; }
        public double getObservedPercentile() { return observedPercentile; }
        public void setObservedPercentile(double v) { this.observedPercentile = v; }
        public Distribution getEnsemble() { return ensemble; }
        public void setEnsemble(Distribution v) { this.ensemble = v; }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Distribution {
        private int n;
        private Map<String, Double> quantiles;
        private Histogram histogram;
        public int getN() { return n; }
        public void setN(int n) { this.n = n; }
        public Map<String, Double> getQuantiles() { return quantiles; }
        public void setQuantiles(Map<String, Double> v) { this.quantiles = v; }
        public Histogram getHistogram() { return histogram; }
        public void setHistogram(Histogram v) { this.histogram = v; }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Histogram {
        @JsonProperty("bin_edges") private List<Double> binEdges;
        private List<Integer> counts;
        public List<Double> getBinEdges() { return binEdges; }
        public void setBinEdges(List<Double> v) { this.binEdges = v; }
        public List<Integer> getCounts() { return counts; }
        public void setCounts(List<Integer> v) { this.counts = v; }
    }
}
