"""Analytics Service for aggregating audit data."""

from typing import List, Dict, Any
import structlog

from app.services.audit_service import AuditService

logger = structlog.get_logger()


class AnalyticsService:
    """Service for analytics aggregations."""
    
    def __init__(self):
        self.audit_service = AuditService()
    
    def get_overview(self) -> Dict[str, Any]:
        """Get analytics overview."""
        try:
            audits = self.audit_service.list_audits(limit=1000)
            
            if not audits:
                return {
                    "total_audits": 0,
                    "avg_score": 0.0,
                    "max_score": 0.0,
                    "min_score": 0.0,
                    "avg_roi": 0.0,
                }
            
            scores = []
            for audit in audits:
                calculated = audit.get("calculated_indices", {})
                score = calculated.get("composite_score", 0)
                if score:
                    scores.append(float(score))
            
            return {
                "total_audits": len(audits),
                "avg_score": sum(scores) / len(scores) if scores else 0.0,
                "max_score": max(scores) if scores else 0.0,
                "min_score": min(scores) if scores else 0.0,
                "avg_roi": sum(a.get("calculated_indices", {}).get("roi_estimate_percent", 0) for a in audits) / len(audits) if audits else 0.0,
            }
        except Exception as e:
            logger.error("analytics_overview_failed", error=str(e))
            return {
                "total_audits": 0,
                "avg_score": 0.0,
                "max_score": 0.0,
                "min_score": 0.0,
                "avg_roi": 0.0,
            }
    
    def get_by_industry(self) -> List[Dict[str, Any]]:
        """Get analytics grouped by industry."""
        try:
            audits = self.audit_service.list_audits(limit=1000)
            
            industry_data = {}
            for audit in audits:
                company = audit.get("company_profile", {})
                industry = company.get("industry", "Unknown")
                calculated = audit.get("calculated_indices", {})
                score = float(calculated.get("composite_score", 0))
                
                if industry not in industry_data:
                    industry_data[industry] = {"scores": [], "count": 0}
                
                industry_data[industry]["scores"].append(score)
                industry_data[industry]["count"] += 1
            
            result = []
            for industry, data in industry_data.items():
                avg_score = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0.0
                result.append({
                    "industry": industry,
                    "count": data["count"],
                    "avg_score": round(avg_score, 2),
                })
            
            return sorted(result, key=lambda x: x["count"], reverse=True)
        except Exception as e:
            logger.error("analytics_by_industry_failed", error=str(e))
            return []
    
    def get_by_level(self) -> List[Dict[str, Any]]:
        """Get analytics grouped by maturity level."""
        try:
            audits = self.audit_service.list_audits(limit=1000)
            
            level_data = {}
            for audit in audits:
                calculated = audit.get("calculated_indices", {})
                level = calculated.get("maturity_level", "Unknown")
                
                if level not in level_data:
                    level_data[level] = 0
                level_data[level] += 1
            
            result = [{"level": level, "count": count} for level, count in level_data.items()]
            return sorted(result, key=lambda x: x["level"])
        except Exception as e:
            logger.error("analytics_by_level_failed", error=str(e))
            return []
    
    def get_top_companies(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top companies by composite score."""
        try:
            audits = self.audit_service.list_audits(limit=1000)
            
            companies = []
            for audit in audits:
                contact = audit.get("contact", {})
                company = audit.get("company_profile", {})
                calculated = audit.get("calculated_indices", {})
                
                score = float(calculated.get("composite_score", 0))
                companies.append({
                    "company_name": contact.get("name", "Unknown"),
                    "industry": company.get("industry", "Unknown"),
                    "score": score,
                    "maturity_level": calculated.get("maturity_level", "Unknown"),
                    "audit_id": audit.get("audit_id"),
                })
            
            return sorted(companies, key=lambda x: x["score"], reverse=True)[:limit]
        except Exception as e:
            logger.error("analytics_top_companies_failed", error=str(e))
            return []

    def get_by_company_size(self) -> List[Dict[str, Any]]:
        """Get analytics grouped by company size."""
        try:
            audits = self.audit_service.list_audits(limit=1000)
            
            size_data = {}
            for audit in audits:
                company = audit.get("company_profile", {})
                size = company.get("company_size", "Unknown")
                calculated = audit.get("calculated_indices", {})
                score = float(calculated.get("composite_score", 0))
                
                if size not in size_data:
                    size_data[size] = {"scores": [], "count": 0}
                
                size_data[size]["scores"].append(score)
                size_data[size]["count"] += 1
            
            result = []
            for size, data in size_data.items():
                avg_score = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0.0
                result.append({
                    "company_size": size,
                    "count": data["count"],
                    "avg_score": round(avg_score, 2),
                })
            
            return sorted(result, key=lambda x: x["company_size"])
        except Exception as e:
            logger.error("analytics_by_company_size_failed", error=str(e))
            return [] 

analytics_service = AnalyticsService()
