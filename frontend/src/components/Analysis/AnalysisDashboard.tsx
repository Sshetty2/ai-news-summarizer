import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { type SentimentAnalysis } from '@/lib/api'
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadialBarChart,
  RadialBar,
  Legend
} from 'recharts'
import {
  TrendingUp,
  TrendingDown,
  Minus,
  BarChart3,
  PieChart as PieChartIcon,
  Target,
  Clock,
  Sparkles
} from 'lucide-react'

interface AnalysisDashboardProps {
  analysis: SentimentAnalysis | null
  isLoading?: boolean
}

const AnalysisDashboard: React.FC<AnalysisDashboardProps> = ({
  analysis,
  isLoading = false
}) => {
  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex justify-center py-12">
          <div className="flex items-center gap-2 text-muted-foreground">
            <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin" />
            <span>Analyzing article...</span>
          </div>
        </div>
      </div>
    )
  }

  if (!analysis) {
    return (
      <div className="text-center text-muted-foreground py-12">
        <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
        <h3 className="text-lg font-semibold mb-2">No Analysis Selected</h3>
        <p className="text-sm">
          Click on an article to view its sentiment analysis
        </p>
      </div>
    )
  }

  // Prepare data for charts
  const sentimentData = [
    { name: 'Positive', value: Math.round(analysis.positive_sentiment * 100), color: '#10b981' },
    { name: 'Negative', value: Math.round(analysis.negative_sentiment * 100), color: '#ef4444' },
    { name: 'Neutral', value: Math.round(analysis.neutral_sentiment * 100), color: '#6b7280' }
  ]

  const topicsData = Object.entries(analysis.topic_distribution)
    .map(([topic, value]) => ({
      topic: topic.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
      value: Math.round((value as number) * 100)
    }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 5)

  const biasScore = analysis.bias_score_normalized
  const biasData = [{
    name: 'Political Bias',
    value: Math.abs(biasScore) * 100,
    fill: biasScore < 0 ? '#ef4444' : biasScore > 0 ? '#3b82f6' : '#6b7280'
  }]

  const getSentimentIcon = () => {
    if (analysis.overall_sentiment_score > 0.1) return <TrendingUp className="h-4 w-4 text-green-600" />
    if (analysis.overall_sentiment_score < -0.1) return <TrendingDown className="h-4 w-4 text-red-600" />
    return <Minus className="h-4 w-4 text-gray-600" />
  }

  return (
    <div className="space-y-4">
      {/* Article Info */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" />
            Analysis Results
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <h3 className="font-semibold text-sm line-clamp-2">
            {analysis.article.title}
          </h3>
          <p className="text-xs text-muted-foreground line-clamp-2">
            {analysis.article.description}
          </p>
          <div className="text-xs text-muted-foreground flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {analysis.created_at}
          </div>
        </CardContent>
      </Card>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 gap-3">
        <Card>
          <CardContent className="pt-4 pb-4">
            <div className="space-y-2">
              <p className="text-xs text-muted-foreground">Political Bias</p>
              <div className="flex items-center justify-between">
                <Badge className={analysis.political_bias}>
                  {analysis.political_bias.replace('_', ' ')}
                </Badge>
                <span className="text-xs text-muted-foreground">
                  {Math.round(analysis.bias_confidence_score * 100)}%
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4 pb-4">
            <div className="space-y-2">
              <p className="text-xs text-muted-foreground">Overall Sentiment</p>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {getSentimentIcon()}
                  <span className="font-semibold text-sm">
                    {analysis.overall_sentiment_score > 0 ? '+' : ''}
                    {(analysis.overall_sentiment_score * 100).toFixed(1)}%
                  </span>
                </div>
                <span className="text-xs text-muted-foreground">
                  {analysis.emotional_tone}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Sentiment Breakdown */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <PieChartIcon className="h-4 w-4" />
            Sentiment
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={sentimentData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={70}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {sentimentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`${value}%`, 'Percentage']} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-3 text-xs">
            {sentimentData.map((entry) => (
              <div key={entry.name} className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
                <span>{entry.name}: {entry.value}%</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Topic Analysis */}
      {topicsData.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Topics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={topicsData} layout="horizontal">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" tick={{ fontSize: 10 }} />
                  <YAxis dataKey="topic" type="category" width={60} tick={{ fontSize: 10 }} />
                  <Tooltip formatter={(value) => [`${value}%`, 'Relevance']} />
                  <Bar dataKey="value" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Key Themes */}
      {analysis.key_themes.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Key Themes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {analysis.key_themes.map((theme, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {theme}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Controversy Level */}
      <Card>
        <CardContent className="pt-4 pb-4">
          <div className="space-y-2">
            <p className="text-xs text-muted-foreground">Controversy Level</p>
            <div className="w-full bg-secondary rounded-full h-2">
              <div
                className="bg-orange-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${analysis.controversy_level * 100}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground text-right">
              {Math.round(analysis.controversy_level * 100)}%
            </p>
          </div>
        </CardContent>
      </Card>

      {/* AI Reasoning */}
      {analysis.bias_reasoning && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">AI Reasoning</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground leading-relaxed">
              {analysis.bias_reasoning}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default AnalysisDashboard
