import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import json
from datetime import datetime
import asyncio
from .audio_analyzer import AudioAnalyzer
from .market_intelligence import MarketIntelligence


class PopularityPredictor:
    """Main popularity prediction service integrating all analysis components"""
    
    def __init__(self):
        self.audio_analyzer = AudioAnalyzer()
        self.market_intelligence = MarketIntelligence()
        
        # Prediction models (simplified - would use ML models in production)
        self.prediction_models = self._initialize_prediction_models()
        
        # Historical data for model training (simplified)
        self.historical_data = self._load_historical_data()
        
        # Performance metrics
        self.model_performance = self._initialize_performance_metrics()
    
    def _initialize_prediction_models(self) -> Dict[str, Dict[str, Any]]:
        """Initialize prediction models"""
        return {
            'popularity_score': {
                'model_type': 'ensemble',
                'components': ['audio_features', 'market_trends', 'pattern_matching'],
                'weights': [0.4, 0.3, 0.3],
                'accuracy': 0.78
            },
            'chart_success': {
                'model_type': 'classification',
                'threshold': 0.75,
                'precision': 0.72,
                'recall': 0.68
            },
            'viral_potential': {
                'model_type': 'regression',
                'features': ['catchiness', 'social_shareability', 'hook_strength'],
                'r_squared': 0.65
            },
            'platform_performance': {
                'model_type': 'multi_output',
                'platforms': ['spotify', 'tiktok', 'radio', 'youtube'],
                'average_accuracy': 0.71
            }
        }
    
    def _load_historical_data(self) -> Dict[str, Any]:
        """Load historical success data for model validation"""
        return {
            'chart_hits': {
                'total_samples': 1000,
                'success_rate': 0.15,
                'avg_features': {
                    'tempo': 125,
                    'energy': 0.75,
                    'danceability': 0.68,
                    'valence': 0.62
                }
            },
            'viral_songs': {
                'total_samples': 500,
                'avg_features': {
                    'catchiness': 0.85,
                    'hook_strength': 0.82,
                    'social_shareability': 0.78
                }
            },
            'streaming_hits': {
                'total_samples': 2000,
                'avg_monthly_streams': 5000000,
                'retention_rate': 0.45
            }
        }
    
    def _initialize_performance_metrics(self) -> Dict[str, float]:
        """Initialize model performance metrics"""
        return {
            'overall_accuracy': 0.74,
            'precision': 0.71,
            'recall': 0.69,
            'f1_score': 0.70,
            'last_updated': datetime.now().timestamp()
        }
    
    async def predict_song_success(
        self,
        audio: np.ndarray,
        lyrics: Optional[str] = None,
        genre: str = 'pop',
        artist_profile: Optional[Dict[str, Any]] = None,
        release_strategy: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Comprehensive song success prediction"""
        
        try:
            # Get comprehensive market intelligence analysis
            market_analysis = await self.market_intelligence.predict_popularity(
                audio=audio,
                lyrics=lyrics,
                genre=genre,
                artist_profile=artist_profile
            )
            
            # Extract key metrics for prediction
            audio_features = market_analysis['audio_analysis']
            trend_alignment = market_analysis['trend_alignment']
            pattern_matching = market_analysis['pattern_matching']
            platform_predictions = market_analysis['platform_predictions']
            
            # Generate specific predictions
            predictions = {}
            
            # Chart success prediction
            predictions['chart_success'] = await self._predict_chart_success(
                audio_features, trend_alignment, pattern_matching
            )
            
            # Viral potential prediction
            predictions['viral_potential'] = await self._predict_viral_potential(
                audio_features, platform_predictions
            )
            
            # Streaming performance prediction
            predictions['streaming_performance'] = await self._predict_streaming_performance(
                audio_features, platform_predictions, genre
            )
            
            # Radio airplay prediction
            predictions['radio_potential'] = await self._predict_radio_potential(
                audio_features, genre
            )
            
            # Social media performance prediction
            predictions['social_media_potential'] = await self._predict_social_media_performance(
                audio_features, platform_predictions
            )
            
            # Commercial success timeline
            predictions['success_timeline'] = await self._predict_success_timeline(
                predictions, release_strategy
            )
            
            # Risk assessment
            risk_analysis = await self._assess_risks(
                market_analysis, predictions, artist_profile
            )
            
            # Generate strategic recommendations
            strategic_recommendations = await self._generate_strategic_recommendations(
                market_analysis, predictions, risk_analysis
            )
            
            # Calculate overall success probability
            overall_success = await self._calculate_overall_success_probability(predictions)
            
            return {
                'prediction_summary': {
                    'overall_success_probability': overall_success['probability'],
                    'confidence_level': overall_success['confidence'],
                    'predicted_peak_position': overall_success['peak_position'],
                    'estimated_total_streams': overall_success['total_streams'],
                    'breakout_probability': overall_success['breakout_probability']
                },
                'detailed_predictions': predictions,
                'market_analysis': market_analysis,
                'risk_analysis': risk_analysis,
                'strategic_recommendations': strategic_recommendations,
                'model_confidence': self._calculate_model_confidence(predictions),
                'prediction_metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'model_version': '1.0',
                    'data_sources': self._get_data_sources_used(),
                    'prediction_horizon': '12_months'
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to predict song success: {str(e)}")
    
    async def _predict_chart_success(
        self,
        audio_features: Dict[str, Any],
        trend_alignment: Dict[str, Any],
        pattern_matching: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict chart success potential"""
        
        # Extract relevant features
        commercial_score = audio_features['commercial']['overall_viability_score']
        trend_score = trend_alignment['overall_alignment']
        chart_pattern_score = pattern_matching['pattern_scores']['chart_potential']['score']
        
        # Calculate chart success probability
        chart_probability = (
            commercial_score * 0.4 +
            trend_score * 0.3 +
            chart_pattern_score * 0.3
        )
        
        # Predict peak position
        if chart_probability > 0.8:
            predicted_peak = np.random.randint(1, 10)  # Top 10
        elif chart_probability > 0.6:
            predicted_peak = np.random.randint(10, 40)  # Top 40
        elif chart_probability > 0.4:
            predicted_peak = np.random.randint(40, 100)  # Top 100
        else:
            predicted_peak = None  # Unlikely to chart
        
        # Time to peak
        time_to_peak = self._estimate_time_to_peak(chart_probability)
        
        # Chart longevity
        chart_longevity = self._estimate_chart_longevity(audio_features, chart_probability)
        
        return {
            'chart_probability': float(chart_probability),
            'predicted_peak_position': predicted_peak,
            'time_to_peak_weeks': time_to_peak,
            'chart_longevity_weeks': chart_longevity,
            'chart_category': self._classify_chart_potential(chart_probability),
            'key_factors': self._identify_chart_success_factors(
                commercial_score, trend_score, chart_pattern_score
            )
        }
    
    async def _predict_viral_potential(
        self,
        audio_features: Dict[str, Any],
        platform_predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict viral potential across platforms"""
        
        # Extract viral indicators
        catchiness = audio_features['perceptual']['catchiness']
        energy = audio_features['perceptual']['energy']
        
        # Platform-specific viral scores
        tiktok_score = platform_predictions['platform_scores']['tiktok']
        instagram_score = platform_predictions['platform_scores']['instagram']
        youtube_shorts_score = platform_predictions['platform_scores']['youtube_shorts']
        
        # Calculate overall viral potential
        viral_potential = (
            catchiness * 0.3 +
            energy * 0.2 +
            tiktok_score * 0.25 +
            instagram_score * 0.15 +
            youtube_shorts_score * 0.1
        )
        
        # Viral timeline prediction
        viral_timeline = self._predict_viral_timeline(viral_potential)
        
        # Viral reach estimation
        viral_reach = self._estimate_viral_reach(viral_potential, platform_predictions)
        
        return {
            'viral_probability': float(viral_potential),
            'viral_category': self._classify_viral_potential(viral_potential),
            'primary_viral_platform': max(
                [('tiktok', tiktok_score), ('instagram', instagram_score), ('youtube_shorts', youtube_shorts_score)],
                key=lambda x: x[1]
            )[0],
            'viral_timeline': viral_timeline,
            'estimated_viral_reach': viral_reach,
            'viral_factors': {
                'catchiness_score': float(catchiness),
                'energy_score': float(energy),
                'platform_readiness': {
                    'tiktok': float(tiktok_score),
                    'instagram': float(instagram_score),
                    'youtube_shorts': float(youtube_shorts_score)
                }
            }
        }
    
    async def _predict_streaming_performance(
        self,
        audio_features: Dict[str, Any],
        platform_predictions: Dict[str, Any],
        genre: str
    ) -> Dict[str, Any]:
        """Predict streaming platform performance"""
        
        # Platform scores
        spotify_score = platform_predictions['platform_scores']['spotify']
        apple_music_score = platform_predictions['platform_scores']['apple_music']
        youtube_music_score = platform_predictions['platform_scores']['youtube_music']
        
        # Audio quality factors
        commercial_score = audio_features['commercial']['overall_viability_score']
        duration = audio_features['basic']['duration']
        
        # Predict monthly streams
        monthly_streams = self._estimate_monthly_streams(
            spotify_score, commercial_score, genre
        )
        
        # Predict playlist inclusion probability
        playlist_probability = self._estimate_playlist_inclusion(
            spotify_score, apple_music_score, genre
        )
        
        # Predict retention metrics
        retention_metrics = self._predict_retention_metrics(
            audio_features, duration
        )
        
        return {
            'platform_performance': {
                'spotify': {
                    'score': float(spotify_score),
                    'estimated_monthly_streams': monthly_streams['spotify'],
                    'playlist_inclusion_probability': playlist_probability['spotify']
                },
                'apple_music': {
                    'score': float(apple_music_score),
                    'estimated_monthly_streams': monthly_streams['apple_music'],
                    'playlist_inclusion_probability': playlist_probability['apple_music']
                },
                'youtube_music': {
                    'score': float(youtube_music_score),
                    'estimated_monthly_streams': monthly_streams['youtube_music']
                }
            },
            'retention_metrics': retention_metrics,
            'streaming_category': self._classify_streaming_potential(
                max(spotify_score, apple_music_score, youtube_music_score)
            ),
            'growth_trajectory': self._predict_streaming_growth(monthly_streams)
        }
    
    async def _predict_radio_potential(
        self,
        audio_features: Dict[str, Any],
        genre: str
    ) -> Dict[str, Any]:
        """Predict radio airplay potential"""
        
        duration = audio_features['basic']['duration']
        commercial_score = audio_features['commercial']['overall_viability_score']
        energy = audio_features['perceptual']['energy']
        
        # Radio-friendly score
        radio_score = self._calculate_radio_friendliness(duration, commercial_score, energy, genre)
        
        # Predict airplay category
        airplay_category = self._classify_radio_potential(radio_score)
        
        # Estimate weekly spins
        weekly_spins = self._estimate_radio_spins(radio_score, genre)
        
        return {
            'radio_potential_score': float(radio_score),
            'airplay_category': airplay_category,
            'estimated_weekly_spins': weekly_spins,
            'radio_format_fit': self._determine_radio_formats(genre, audio_features),
            'peak_airplay_timeline': self._predict_radio_timeline(radio_score)
        }
    
    async def _predict_social_media_performance(
        self,
        audio_features: Dict[str, Any],
        platform_predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict social media performance"""
        
        platform_scores = platform_predictions['platform_scores']
        
        # Social media metrics
        social_metrics = {}
        
        for platform in ['tiktok', 'instagram', 'youtube']:
            if platform in platform_scores:
                score = platform_scores[platform]
                social_metrics[platform] = {
                    'engagement_score': float(score),
                    'estimated_posts': self._estimate_social_posts(score, platform),
                    'viral_probability': self._calculate_platform_viral_probability(score),
                    'growth_potential': self._assess_social_growth_potential(score, platform)
                }
        
        return {
            'platform_metrics': social_metrics,
            'overall_social_score': np.mean([s['engagement_score'] for s in social_metrics.values()]),
            'best_social_platform': max(social_metrics.items(), key=lambda x: x[1]['engagement_score'])[0],
            'social_strategy_recommendations': self._generate_social_strategy(social_metrics)
        }
    
    async def _predict_success_timeline(
        self,
        predictions: Dict[str, Any],
        release_strategy: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Predict success timeline and milestones"""
        
        timeline = {
            'week_1': {
                'streaming_momentum': 'building',
                'social_media_activity': 'high',
                'radio_consideration': 'initial'
            },
            'month_1': {
                'chart_entry_probability': predictions.get('chart_success', {}).get('chart_probability', 0) * 0.7,
                'viral_peak_probability': predictions.get('viral_potential', {}).get('viral_probability', 0) * 0.8,
                'playlist_additions': 'moderate'
            },
            'month_3': {
                'peak_performance_window': True,
                'radio_saturation': 'building',
                'international_expansion': 'possible'
            },
            'month_6': {
                'longevity_assessment': 'stable' if predictions.get('chart_success', {}).get('chart_longevity_weeks', 0) > 12 else 'declining',
                'catalog_value': 'established'
            }
        }
        
        # Adjust timeline based on release strategy
        if release_strategy:
            timeline = self._adjust_timeline_for_strategy(timeline, release_strategy)
        
        return timeline
    
    async def _assess_risks(
        self,
        market_analysis: Dict[str, Any],
        predictions: Dict[str, Any],
        artist_profile: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess risks and potential challenges"""
        
        risks = {
            'market_risks': [],
            'competitive_risks': [],
            'technical_risks': [],
            'strategic_risks': []
        }
        
        # Market risks
        trend_alignment = market_analysis['trend_alignment']['overall_alignment']
        if trend_alignment < 0.5:
            risks['market_risks'].append({
                'risk': 'Poor trend alignment',
                'severity': 'high',
                'mitigation': 'Consider updating production style'
            })
        
        # Competitive risks
        market_insights = market_analysis['market_insights']
        if market_insights['competitive_landscape']['competition_level'] == 'high':
            risks['competitive_risks'].append({
                'risk': 'High market competition',
                'severity': 'medium',
                'mitigation': 'Focus on unique positioning'
            })
        
        # Technical risks
        audio_quality = market_analysis['audio_analysis']['commercial']['overall_viability_score']
        if audio_quality < 0.6:
            risks['technical_risks'].append({
                'risk': 'Below-average production quality',
                'severity': 'high',
                'mitigation': 'Improve mixing and mastering'
            })
        
        # Strategic risks
        if not artist_profile or artist_profile.get('social_score', 0) < 0.4:
            risks['strategic_risks'].append({
                'risk': 'Limited social media presence',
                'severity': 'medium',
                'mitigation': 'Develop social media strategy'
            })
        
        # Calculate overall risk score
        total_risks = sum(len(risk_list) for risk_list in risks.values())
        risk_score = min(1.0, total_risks / 10)  # Normalize to 0-1
        
        return {
            'risk_categories': risks,
            'overall_risk_score': float(risk_score),
            'risk_level': self._classify_risk_level(risk_score),
            'priority_mitigations': self._prioritize_risk_mitigations(risks)
        }
    
    async def _generate_strategic_recommendations(
        self,
        market_analysis: Dict[str, Any],
        predictions: Dict[str, Any],
        risk_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate strategic recommendations for maximizing success"""
        
        recommendations = []
        
        # Based on predictions
        chart_probability = predictions.get('chart_success', {}).get('chart_probability', 0)
        if chart_probability > 0.7:
            recommendations.append({
                'category': 'promotion',
                'priority': 'high',
                'recommendation': 'Invest in radio promotion campaign',
                'expected_impact': 'high',
                'timeline': 'pre_release'
            })
        
        viral_probability = predictions.get('viral_potential', {}).get('viral_probability', 0)
        if viral_probability > 0.6:
            recommendations.append({
                'category': 'social_media',
                'priority': 'high',
                'recommendation': 'Create TikTok-first marketing campaign',
                'expected_impact': 'high',
                'timeline': 'release_week'
            })
        
        # Based on market analysis
        best_platforms = market_analysis['platform_predictions']['best_platforms']
        for platform, score in best_platforms:
            if score > 0.7:
                recommendations.append({
                    'category': 'platform_focus',
                    'priority': 'medium',
                    'recommendation': f'Prioritize {platform} for initial push',
                    'expected_impact': 'medium',
                    'timeline': 'release_month'
                })
        
        # Based on risk analysis
        for mitigation in risk_analysis['priority_mitigations']:
            recommendations.append({
                'category': 'risk_mitigation',
                'priority': mitigation['priority'],
                'recommendation': mitigation['action'],
                'expected_impact': 'medium',
                'timeline': 'immediate'
            })
        
        # Genre-specific recommendations
        recommendations.extend(market_analysis['recommendations'])
        
        return recommendations
    
    async def _calculate_overall_success_probability(
        self,
        predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate overall success probability and metrics"""
        
        # Weight different success metrics
        weights = {
            'chart_success': 0.25,
            'streaming_performance': 0.30,
            'viral_potential': 0.20,
            'radio_potential': 0.15,
            'social_media_potential': 0.10
        }
        
        # Extract scores
        chart_score = predictions.get('chart_success', {}).get('chart_probability', 0)
        streaming_score = max([
            p.get('score', 0) for p in 
            predictions.get('streaming_performance', {}).get('platform_performance', {}).values()
        ]) if predictions.get('streaming_performance') else 0
        viral_score = predictions.get('viral_potential', {}).get('viral_probability', 0)
        radio_score = predictions.get('radio_potential', {}).get('radio_potential_score', 0)
        social_score = predictions.get('social_media_potential', {}).get('overall_social_score', 0)
        
        # Calculate weighted average
        overall_probability = (
            chart_score * weights['chart_success'] +
            streaming_score * weights['streaming_performance'] +
            viral_score * weights['viral_potential'] +
            radio_score * weights['radio_potential'] +
            social_score * weights['social_media_potential']
        )
        
        # Estimate other metrics
        confidence = self._calculate_prediction_confidence(predictions)
        peak_position = self._estimate_peak_chart_position(overall_probability)
        total_streams = self._estimate_total_streams(overall_probability, streaming_score)
        breakout_probability = self._calculate_breakout_probability(viral_score, chart_score)
        
        return {
            'probability': float(overall_probability),
            'confidence': float(confidence),
            'peak_position': peak_position,
            'total_streams': total_streams,
            'breakout_probability': float(breakout_probability)
        }
    
    # Helper methods (simplified implementations)
    
    def _estimate_time_to_peak(self, chart_probability: float) -> int:
        """Estimate weeks to reach peak chart position"""
        if chart_probability > 0.8:
            return np.random.randint(2, 6)  # Fast climbers
        elif chart_probability > 0.6:
            return np.random.randint(4, 10)  # Steady climbers
        else:
            return np.random.randint(8, 16)  # Slow burns
    
    def _estimate_chart_longevity(self, audio_features: Dict[str, Any], chart_probability: float) -> int:
        """Estimate weeks on chart"""
        base_longevity = int(chart_probability * 20)  # Base weeks
        
        # Adjust for catchiness
        catchiness = audio_features['perceptual']['catchiness']
        longevity_bonus = int(catchiness * 10)
        
        return base_longevity + longevity_bonus
    
    def _classify_chart_potential(self, probability: float) -> str:
        """Classify chart potential"""
        if probability > 0.8:
            return 'high_potential'
        elif probability > 0.6:
            return 'moderate_potential'
        elif probability > 0.4:
            return 'low_potential'
        else:
            return 'unlikely'
    
    def _identify_chart_success_factors(
        self,
        commercial_score: float,
        trend_score: float,
        pattern_score: float
    ) -> List[str]:
        """Identify key factors for chart success"""
        factors = []
        
        if commercial_score > 0.7:
            factors.append('strong_commercial_appeal')
        if trend_score > 0.7:
            factors.append('trend_alignment')
        if pattern_score > 0.7:
            factors.append('proven_success_patterns')
        
        return factors
    
    def _predict_viral_timeline(self, viral_potential: float) -> Dict[str, str]:
        """Predict viral timeline"""
        if viral_potential > 0.8:
            return {
                'initial_spark': 'days_1_3',
                'peak_virality': 'week_1',
                'sustained_buzz': 'weeks_2_4'
            }
        elif viral_potential > 0.6:
            return {
                'initial_spark': 'week_1',
                'peak_virality': 'weeks_2_3',
                'sustained_buzz': 'weeks_4_8'
            }
        else:
            return {
                'initial_spark': 'weeks_2_4',
                'peak_virality': 'month_2',
                'sustained_buzz': 'limited'
            }
    
    def _estimate_viral_reach(
        self,
        viral_potential: float,
        platform_predictions: Dict[str, Any]
    ) -> Dict[str, int]:
        """Estimate viral reach across platforms"""
        base_reach = int(viral_potential * 10000000)  # Base reach
        
        return {
            'tiktok': int(base_reach * platform_predictions['platform_scores'].get('tiktok', 0.5)),
            'instagram': int(base_reach * platform_predictions['platform_scores'].get('instagram', 0.5) * 0.8),
            'youtube_shorts': int(base_reach * platform_predictions['platform_scores'].get('youtube_shorts', 0.5) * 0.6),
            'total_estimated': base_reach
        }
    
    def _classify_viral_potential(self, potential: float) -> str:
        """Classify viral potential"""
        if potential > 0.8:
            return 'high_viral_potential'
        elif potential > 0.6:
            return 'moderate_viral_potential'
        elif potential > 0.4:
            return 'low_viral_potential'
        else:
            return 'minimal_viral_potential'
    
    def _estimate_monthly_streams(
        self,
        spotify_score: float,
        commercial_score: float,
        genre: str
    ) -> Dict[str, int]:
        """Estimate monthly streams by platform"""
        
        # Base streams calculation
        base_streams = int((spotify_score + commercial_score) / 2 * 1000000)
        
        # Genre multipliers
        genre_multipliers = {
            'pop': 1.2,
            'hip_hop': 1.1,
            'rock': 0.9,
            'electronic': 1.0,
            'r&b': 0.8
        }
        
        multiplier = genre_multipliers.get(genre.lower(), 1.0)
        
        return {
            'spotify': int(base_streams * multiplier * 0.4),  # Spotify market share
            'apple_music': int(base_streams * multiplier * 0.25),
            'youtube_music': int(base_streams * multiplier * 0.2)
        }
    
    def _estimate_playlist_inclusion(
        self,
        spotify_score: float,
        apple_music_score: float,
        genre: str
    ) -> Dict[str, float]:
        """Estimate playlist inclusion probability"""
        return {
            'spotify': min(0.95, spotify_score * 0.8),
            'apple_music': min(0.95, apple_music_score * 0.7)
        }
    
    def _predict_retention_metrics(
        self,
        audio_features: Dict[str, Any],
        duration: float
    ) -> Dict[str, float]:
        """Predict listener retention metrics"""
        
        catchiness = audio_features['perceptual']['catchiness']
        energy = audio_features['perceptual']['energy']
        
        # Skip rate (lower is better)
        skip_rate = max(0.1, 1.0 - (catchiness + energy) / 2)
        
        # Completion rate
        completion_rate = min(0.9, (catchiness * 0.6 + energy * 0.4))
        
        # Replay rate
        replay_rate = min(0.5, catchiness * 0.8)
        
        return {
            'skip_rate': float(skip_rate),
            'completion_rate': float(completion_rate),
            'replay_rate': float(replay_rate),
            'save_rate': float(completion_rate * 0.3)  # Estimated save rate
        }
    
    def _classify_streaming_potential(self, max_score: float) -> str:
        """Classify streaming potential"""
        if max_score > 0.8:
            return 'streaming_hit_potential'
        elif max_score > 0.6:
            return 'solid_streaming_performance'
        elif max_score > 0.4:
            return 'moderate_streaming_appeal'
        else:
            return 'limited_streaming_potential'
    
    def _predict_streaming_growth(self, monthly_streams: Dict[str, int]) -> str:
        """Predict streaming growth trajectory"""
        total_streams = sum(monthly_streams.values())
        
        if total_streams > 5000000:
            return 'exponential_growth'
        elif total_streams > 1000000:
            return 'steady_growth'
        elif total_streams > 100000:
            return 'gradual_growth'
        else:
            return 'slow_growth'
    
    def _calculate_radio_friendliness(
        self,
        duration: float,
        commercial_score: float,
        energy: float,
        genre: str
    ) -> float:
        """Calculate radio-friendliness score"""
        
        # Duration score (radio prefers 3-4 minutes)
        duration_score = 1.0 if 180 <= duration <= 240 else 0.7
        
        # Commercial appeal
        commercial_factor = commercial_score
        
        # Energy level (radio prefers moderate to high energy)
        energy_factor = min(1.0, energy * 1.2)
        
        # Genre factor
        genre_factors = {
            'pop': 1.0,
            'rock': 0.8,
            'hip_hop': 0.7,
            'country': 0.9,
            'r&b': 0.8
        }
        genre_factor = genre_factors.get(genre.lower(), 0.6)
        
        return (duration_score * 0.3 + commercial_factor * 0.4 + energy_factor * 0.2 + genre_factor * 0.1)
    
    def _classify_radio_potential(self, radio_score: float) -> str:
        """Classify radio potential"""
        if radio_score > 0.8:
            return 'high_rotation_potential'
        elif radio_score > 0.6:
            return 'moderate_airplay_potential'
        elif radio_score > 0.4:
            return 'limited_airplay_potential'
        else:
            return 'minimal_airplay_potential'
    
    # Additional helper methods (simplified implementations)
    
    def _estimate_radio_spins(self, radio_score: float, genre: str) -> int:
        """Estimate weekly radio spins"""
        base_spins = int(radio_score * 1000)
        genre_multipliers = {'pop': 1.2, 'rock': 1.0, 'hip_hop': 0.8, 'country': 1.1}
        multiplier = genre_multipliers.get(genre.lower(), 0.9)
        return int(base_spins * multiplier)
    
    def _determine_radio_formats(self, genre: str, audio_features: Dict[str, Any]) -> List[str]:
        """Determine suitable radio formats"""
        formats = []
        if genre.lower() == 'pop':
            formats.extend(['top_40', 'adult_contemporary'])
        elif genre.lower() == 'rock':
            formats.extend(['rock', 'alternative'])
        elif genre.lower() == 'hip_hop':
            formats.extend(['urban', 'rhythmic'])
        return formats
    
    def _predict_radio_timeline(self, radio_score: float) -> Dict[str, str]:
        """Predict radio airplay timeline"""
        if radio_score > 0.7:
            return {'add_date': 'week_2', 'peak_airplay': 'week_8', 'chart_impact': 'week_12'}
        else:
            return {'add_date': 'week_4', 'peak_airplay': 'week_16', 'chart_impact': 'week_20'}
    
    def _estimate_social_posts(self, score: float, platform: str) -> int:
        """Estimate number of social media posts"""
        base_posts = int(score * 10000)
        platform_multipliers = {'tiktok': 2.0, 'instagram': 1.5, 'youtube': 1.0}
        multiplier = platform_multipliers.get(platform, 1.0)
        return int(base_posts * multiplier)
    
    def _calculate_platform_viral_probability(self, score: float) -> float:
        """Calculate platform-specific viral probability"""
        return min(0.95, score * 1.2)
    
    def _assess_social_growth_potential(self, score: float, platform: str) -> str:
        """Assess social media growth potential"""
        if score > 0.8:
            return 'high_growth'
        elif score > 0.6:
            return 'moderate_growth'
        else:
            return 'limited_growth'
    
    def _generate_social_strategy(self, social_metrics: Dict[str, Any]) -> List[str]:
        """Generate social media strategy recommendations"""
        strategies = []
        best_platform = max(social_metrics.items(), key=lambda x: x[1]['engagement_score'])[0]
        strategies.append(f'Focus initial efforts on {best_platform}')
        strategies.append('Create platform-specific content')
        strategies.append('Engage with trending hashtags')
        return strategies
    
    def _adjust_timeline_for_strategy(
        self,
        timeline: Dict[str, Any],
        release_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adjust timeline based on release strategy"""
        # Simplified timeline adjustment
        return timeline
    
    def _classify_risk_level(self, risk_score: float) -> str:
        """Classify overall risk level"""
        if risk_score > 0.7:
            return 'high_risk'
        elif risk_score > 0.4:
            return 'moderate_risk'
        else:
            return 'low_risk'
    
    def _prioritize_risk_mitigations(self, risks: Dict[str, List]) -> List[Dict[str, str]]:
        """Prioritize risk mitigations"""
        mitigations = []
        for category, risk_list in risks.items():
            for risk in risk_list:
                mitigations.append({
                    'category': category,
                    'action': risk['mitigation'],
                    'priority': risk['severity']
                })
        return sorted(mitigations, key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['priority']], reverse=True)
    
    def _calculate_model_confidence(self, predictions: Dict[str, Any]) -> float:
        """Calculate overall model confidence"""
        # Simplified confidence calculation based on prediction consistency
        scores = []
        for prediction_type, prediction_data in predictions.items():
            if isinstance(prediction_data, dict):
                for key, value in prediction_data.items():
                    if isinstance(value, (int, float)) and 0 <= value <= 1:
                        scores.append(value)
        
        if scores:
            variance = np.var(scores)
            confidence = max(0.3, 1.0 - variance)  # Lower variance = higher confidence
            return min(0.95, confidence)
        return 0.7  # Default confidence
    
    def _get_data_sources_used(self) -> List[str]:
        """Get list of data sources used in prediction"""
        return [
            'audio_feature_analysis',
            'market_trend_data',
            'historical_success_patterns',
            'platform_performance_metrics',
            'genre_specific_models'
        ]
    
    def _calculate_prediction_confidence(self, predictions: Dict[str, Any]) -> float:
        """Calculate prediction confidence level"""
        # Base confidence on model performance and prediction consistency
        base_confidence = self.model_performance['overall_accuracy']
        
        # Adjust based on prediction spread
        scores = []
        for pred_type, pred_data in predictions.items():
            if isinstance(pred_data, dict):
                for key, value in pred_data.items():
                    if isinstance(value, (int, float)) and 0 <= value <= 1:
                        scores.append(value)
        
        if scores:
            score_std = np.std(scores)
            confidence_adjustment = max(-0.2, -score_std)  # Penalize high variance
            return max(0.3, min(0.95, base_confidence + confidence_adjustment))
        
        return base_confidence
    
    def _estimate_peak_chart_position(self, overall_probability: float) -> Optional[int]:
        """Estimate peak chart position"""
        if overall_probability > 0.8:
            return np.random.randint(1, 10)
        elif overall_probability > 0.6:
            return np.random.randint(10, 40)
        elif overall_probability > 0.4:
            return np.random.randint(40, 100)
        else:
            return None
    
    def _estimate_total_streams(self, overall_probability: float, streaming_score: float) -> int:
        """Estimate total streams over 12 months"""
        base_streams = int(overall_probability * streaming_score * 50000000)
        return max(10000, base_streams)
    
    def _calculate_breakout_probability(self, viral_score: float, chart_score: float) -> float:
        """Calculate probability of breakout success"""
        breakout_threshold = 0.7
        combined_score = (viral_score * 0.6 + chart_score * 0.4)
        
        if combined_score > breakout_threshold:
            return min(0.95, combined_score * 1.2)
        else:
            return combined_score * 0.5
