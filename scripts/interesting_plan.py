def calculate_split(plan, incumbent_mappings):
    precincts = plan.graph.nodes
    dem_winners = 0
    rep_winners = 0
    for incumbent in incumbent_mappings:
        mapping = incumbent_mappings[incumbent]
        district = mapping["id_new"]
        dem_votes = sum([precincts[precinct]["democrat"] for precinct in plan.parts[district]])
        rep_votes = sum([precincts[precinct]["republican"] for precinct in plan.parts[district]])
        party = incumbent_mappings[incumbent]["incumbent_party"]
        if dem_votes > rep_votes and party == "D":
            dem_winners += 1
        elif rep_votes > dem_votes and party == "R":
            rep_winners += 1
    return dem_winners, rep_winners
def analyze_seats(plan, incumbent_mappings, interesting_criteria, interesting_plans):
    dem_winners, rep_winners = calculate_split(plan, incumbent_mappings)
    dem_votes = sum([plan.graph.nodes[precinct]["democrat"] for precinct in plan.graph.nodes])
    rep_votes = sum([plan.graph.nodes[precinct]["republican"] for precinct in plan.graph.nodes])
    seat_vote_difference = abs((dem_votes / (dem_votes + rep_votes)) - (dem_winners / (dem_winners + rep_winners)))
    if seat_vote_difference < interesting_criteria["fairest_seat_vote"]:
        interesting_criteria["fairest_seat_vote"] = seat_vote_difference
        interesting_plans["fair_seat_vote"] = plan
    if dem_winners - rep_winners > interesting_criteria["most_democrat_favored"]:
        interesting_criteria["most_democrat_favored"] = dem_winners - rep_winners
        interesting_plans["democrat_favored"] = plan
    if rep_winners - dem_winners > interesting_criteria["most_republican_favored"]:
        interesting_criteria["most_republican_favored"] = rep_winners - dem_winners
        interesting_plans["republican_favored"] = plan
def analyze_geo_pop_var(plan_20, plan_new, incumbent_mappings, interesting_criteria, interesting_plans):
    total_geo_pop_var = 0
    dem_geo_pop_var = 0
    rep_geo_pop_var = 0
    for incumbent in incumbent_mappings:
        id_20 = incumbent_mappings[incumbent]["id_20"]
        id_new = incumbent_mappings[incumbent]["id_new"]
        intersection = plan_20.parts[id_20].intersection(plan_new.parts[id_new])
        area_common = sum([plan_new.graph.nodes[x]['area'] for x in intersection])
        area_total = sum([plan_new.graph.nodes[x]['area'] for x in plan_new.parts[id_new]])
        area_added = area_total - area_common
        area_variation = area_added / area_total
        pop_common = sum([plan_new.graph.nodes[x]['vap_total'] for x in intersection])
        pop_total = sum([plan_new.graph.nodes[x]['vap_total'] for x in plan_new.parts[id_new]])
        pop_added = pop_total - pop_common
        pop_variation = pop_added / pop_total
        total_geo_pop_var += area_variation + pop_variation
        if incumbent_mappings[incumbent]["incumbent_party"] == "D":
            dem_geo_pop_var += area_variation + pop_variation
        else:
            rep_geo_pop_var += area_variation + pop_variation
    if total_geo_pop_var > interesting_criteria["highest_geo_pop_var"]:
        interesting_criteria["highest_geo_pop_var"] = total_geo_pop_var
        interesting_plans["high_geo_pop_var"] = plan_new
    geo_pop_var_fairness = abs((dem_geo_pop_var - rep_geo_pop_var) / total_geo_pop_var)
    if geo_pop_var_fairness < interesting_criteria["fairest_geo_pop_var"]:
        interesting_criteria["fairest_geo_pop_var"] = geo_pop_var_fairness
        interesting_plans["fair_geo_pop_var"] = plan_new
def find_interesting_plans(plan_20, plan_new, incumbent_mappings, interesting_criteria, interesting_plans):
    analyze_seats(plan_new, incumbent_mappings, interesting_criteria, interesting_plans)
    analyze_geo_pop_var(plan_20, plan_new, incumbent_mappings, interesting_criteria, interesting_plans)