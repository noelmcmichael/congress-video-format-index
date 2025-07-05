# Congress Video Format Index - Analysis Report
Generated: 2025-07-05 00:11:17

## Database Statistics

- **Total Committees**: 47
- **Total Subcommittees**: 0
- **Total Hearings**: 17
- **Total Video Formats**: 0

## Committees by Chamber

| Chamber | Count |
|---------|-------|
| House | 23 |
| Senate | 24 |

## House of Representatives Committees

| Committee | Code | Official URL |
|-----------|------|--------------|
| Agriculture | AGRICULTURE | [https://agriculture.house.gov/](https://agriculture.house.gov/) |
| Appropriations | APPROPRIATIONS | [https://appropriations.house.gov/](https://appropriations.house.gov/) |
| Armed Services | ARMEDSERVICES | [https://armedservices.house.gov/](https://armedservices.house.gov/) |
| Budget | BUDGET | [https://budget.house.gov/](https://budget.house.gov/) |
| Education and Workforce | EDWORKFORCE | [https://edworkforce.house.gov/](https://edworkforce.house.gov/) |
| Energy and Commerce | ENERGYCOMMERCE | [https://energycommerce.house.gov/](https://energycommerce.house.gov/) |
| Ethics | ETHICS | [https://ethics.house.gov/](https://ethics.house.gov/) |
| Financial Services | FINANCIALSERVICES | [https://financialservices.house.gov/](https://financialservices.house.gov/) |
| Foreign Affairs | FOREIGNAFFAIRS | [https://foreignaffairs.house.gov/](https://foreignaffairs.house.gov/) |
| House Administration | CHA | [https://cha.house.gov/](https://cha.house.gov/) |
| Joint Committee on Printing | CHA | [https://cha.house.gov/joint-committee-on-printing](https://cha.house.gov/joint-committee-on-printing) |
| Joint Committee on the Library | CHA | [https://cha.house.gov/joint-committee-on-library](https://cha.house.gov/joint-committee-on-library) |
| Judiciary | JUDICIARY | [https://judiciary.house.gov/](https://judiciary.house.gov/) |
| Natural Resources | NATURALRESOURCES | [https://naturalresources.house.gov/](https://naturalresources.house.gov/) |
| Oversight and Government Reform | OVERSIGHT | [https://oversight.house.gov/](https://oversight.house.gov/) |
| Permanent Select Committee on Intelligence | INTELLIGENCE | [https://intelligence.house.gov/](https://intelligence.house.gov/) |
| Rules | RULES | [https://rules.house.gov/](https://rules.house.gov/) |
| Science, Space, and Technology | SCIENCE | [https://science.house.gov/](https://science.house.gov/) |
| Select Committee on the Strategic Competition Between the United States and the Chinese Communist Party | SELECTCOMMITTEEONTHECCP | [https://selectcommitteeontheccp.house.gov/](https://selectcommitteeontheccp.house.gov/) |
| Small Business | SMALLBUSINESS | [https://smallbusiness.house.gov/](https://smallbusiness.house.gov/) |
| Transportation and Infrastructure | TRANSPORTATION | [https://transportation.house.gov/](https://transportation.house.gov/) |
| Veterans’ Affairs | VETERANS | [https://veterans.house.gov/](https://veterans.house.gov/) |
| Ways and Means | WAYSANDMEANS | [https://waysandmeans.house.gov/](https://waysandmeans.house.gov/) |

## Senate Committees

| Committee | Code | Official URL |
|-----------|------|--------------|
| Agriculture, Nutrition, and Forestry | ANA | [http://www.agriculture.senate.gov/](http://www.agriculture.senate.gov/) |
| Appropriations | N/A | [http://www.appropriations.senate.gov/](http://www.appropriations.senate.gov/) |
| Armed Services | AS | [http://www.armed-services.senate.gov/](http://www.armed-services.senate.gov/) |
| Banking, Housing, and Urban Affairs | BHA | [http://www.banking.senate.gov/public](http://www.banking.senate.gov/public) |
| Budget | N/A | [http://www.budget.senate.gov/](http://www.budget.senate.gov/) |
| Commerce, Science, and Transportation | CSA | [http://www.commerce.senate.gov/](http://www.commerce.senate.gov/) |
| Energy and Natural Resources | EAN | [http://www.energy.senate.gov/](http://www.energy.senate.gov/) |
| Environment and Public Works | EAP | [http://www.epw.senate.gov/](http://www.epw.senate.gov/) |
| Finance | N/A | [http://www.finance.senate.gov/](http://www.finance.senate.gov/) |
| Foreign Relations | FR | [http://www.foreign.senate.gov/](http://www.foreign.senate.gov/) |
| Health, Education, Labor, and Pensions | HEL | [http://www.help.senate.gov/](http://www.help.senate.gov/) |
| Homeland Security and Governmental Affairs | HSA | [http://www.hsgac.senate.gov/](http://www.hsgac.senate.gov/) |
| Indian Affairs | IA | [http://www.indian.senate.gov/](http://www.indian.senate.gov/) |
| Joint Committee on Printing | WWW | [http://www.senate.gov/general/committee_membership/committee_memberships_JSPR.htm](http://www.senate.gov/general/committee_membership/committee_memberships_JSPR.htm) |
| Joint Committee on Taxation | N/A | [https://www.jct.gov/](https://www.jct.gov/) |
| Joint Committee on the Library | WWW | [http://www.senate.gov/general/committee_membership/committee_memberships_JSLC.htm](http://www.senate.gov/general/committee_membership/committee_memberships_JSLC.htm) |
| Joint Economic Committee | JEC | [http://www.jec.senate.gov/](http://www.jec.senate.gov/) |
| Judiciary | N/A | [http://www.judiciary.senate.gov/](http://www.judiciary.senate.gov/) |
| Rules and Administration | RAA | [http://www.rules.senate.gov/](http://www.rules.senate.gov/) |
| Select Committee on Ethics | SCO | [http://www.ethics.senate.gov/](http://www.ethics.senate.gov/) |
| Select Committee on Intelligence | SCO | [http://www.intelligence.senate.gov/](http://www.intelligence.senate.gov/) |
| Small Business and Entrepreneurship | SBA | [http://www.sbc.senate.gov/](http://www.sbc.senate.gov/) |
| Special Committee on Aging | SCO | [http://www.aging.senate.gov](http://www.aging.senate.gov) |
| Veterans' Affairs | VA | [http://www.veterans.senate.gov/](http://www.veterans.senate.gov/) |

## Technical Findings

### Website Architecture

**House of Representatives:**
- Uses decentralized committee websites
- Each committee has its own subdomain (e.g., agriculture.house.gov)
- Total unique domains: 21

**Senate:**
- Uses centralized committee directory
- Mixed approach with both senate.gov and external domains
- Total unique domains: 23

### Scraping Challenges Identified

1. **Inconsistent Website Structures**: Each committee uses different layouts
2. **Rate Limiting**: Some sites implement aggressive rate limiting
3. **JavaScript Dependencies**: Some video players require JavaScript execution
4. **Access Restrictions**: Some committee sites block automated access
5. **Video Format Detection**: Complex embed codes and custom players

## Recommendations

### For Researchers
- Focus on Senate committees for more consistent data access
- House committees require individual analysis due to decentralized structure
- Video format detection works best on sites with standard embed codes

### For Congress
- Standardize video streaming platforms across committees
- Implement consistent accessibility features
- Provide structured data feeds for hearing information
- Consider centralized video hosting solution

## Data Quality Notes

- **Committee Discovery**: High accuracy for both chambers
- **Hearing Detection**: Variable success rate due to site differences
- **Video Format Detection**: Limited by JavaScript-heavy implementations
- **Real-time Data**: Snapshot from scraping session, not live data

## Future Work

1. **Enhanced Video Detection**: Implement Selenium for JavaScript-heavy sites
2. **Real-time Monitoring**: Set up scheduled scraping for live data
3. **Accessibility Analysis**: Evaluate compliance with accessibility standards
4. **Performance Metrics**: Measure video quality and streaming reliability
5. **API Development**: Create public API for accessing the data

## Appendix

### Data Sources
- House: https://www.house.gov/committees
- Senate: https://www.senate.gov/committees/

### Technology Stack
- **Language**: Python 3.13+
- **Web Scraping**: BeautifulSoup, Requests, Selenium
- **Database**: SQLite3
- **Analysis**: Pandas, SQLite
