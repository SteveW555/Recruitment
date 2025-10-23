"""
Chart Generator - Create interactive visualizations using Plotly.

Generates bar charts, line charts, and pie charts from pandas DataFrames.
Outputs interactive HTML files with hover tooltips, zoom, and pan capabilities.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List
import structlog


logger = structlog.get_logger()


class ChartGenerator:
    """
    Generate interactive charts using Plotly.

    Supports:
    - Bar charts (comparison, grouped)
    - Line charts (trends over time)
    - Pie charts (composition, donut)
    - Combination charts

    Outputs:
    - Interactive HTML files (hover, zoom, pan)
    - Static PNG/SVG exports (optional)
    """

    def __init__(self, output_dir: str = "./generated_charts"):
        """
        Initialize ChartGenerator.

        Args:
            output_dir: Directory to save generated charts
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Default color schemes
        self.color_schemes = {
            'blue': ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78'],
            'green': ['#2ca02c', '#98df8a', '#d62728', '#ff9896'],
            'professional': ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b'],
            'recruitment': ['#0ea5e9', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981']
        }

        logger.info("chart_generator_initialized", output_dir=str(self.output_dir))

    def bar_chart(
        self,
        data: pd.DataFrame,
        x_column: str,
        y_column: str,
        title: str,
        output_filename: str,
        color_scheme: str = 'professional',
        orientation: str = 'v',
        show_values: bool = True
    ) -> Dict[str, str]:
        """
        Generate a bar chart from DataFrame.

        Args:
            data: Pandas DataFrame with data
            x_column: Column name for X-axis
            y_column: Column name for Y-axis
            title: Chart title
            output_filename: Output filename (without extension)
            color_scheme: Color scheme to use
            orientation: 'v' (vertical) or 'h' (horizontal)
            show_values: Show values on bars

        Returns:
            Dict with 'html_path' and 'png_path'
        """
        try:
            fig = px.bar(
                data,
                x=x_column,
                y=y_column,
                title=title,
                template='plotly_white',
                orientation=orientation,
                color=y_column if orientation == 'v' else x_column,
                color_continuous_scale='Blues'
            )

            # Customize layout
            fig.update_layout(
                font=dict(size=14, family='Arial, sans-serif'),
                title_font_size=20,
                title_font_color='#1f2937',
                xaxis_title=x_column.replace('_', ' ').title(),
                yaxis_title=y_column.replace('_', ' ').title(),
                hovermode='closest',
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=60, r=40, t=80, b=60),
                height=500
            )

            # Add value labels on bars
            if show_values:
                fig.update_traces(
                    texttemplate='%{y:,.0f}' if orientation == 'v' else '%{x:,.0f}',
                    textposition='outside'
                )

            # Customize hover template
            fig.update_traces(
                hovertemplate='<b>%{x}</b><br>Amount: £%{y:,.2f}<extra></extra>'
                if orientation == 'v' else
                '<b>%{y}</b><br>Amount: £%{x:,.2f}<extra></extra>'
            )

            # Save files
            html_path = self.output_dir / f"{output_filename}.html"
            png_path = self.output_dir / f"{output_filename}.png"

            fig.write_html(html_path)

            # Try to save PNG (requires kaleido)
            try:
                fig.write_image(png_path, width=1200, height=600, scale=2)
            except Exception as e:
                logger.warning("png_export_failed", error=str(e))
                png_path = None

            logger.info("bar_chart_generated", title=title, html_path=str(html_path))

            return {
                'html_path': str(html_path),
                'png_path': str(png_path) if png_path else None,
                'title': title,
                'type': 'bar'
            }

        except Exception as e:
            logger.error("bar_chart_generation_failed", error=str(e), title=title)
            raise

    def line_chart(
        self,
        data: pd.DataFrame,
        x_column: str,
        y_column: str,
        title: str,
        output_filename: str,
        show_markers: bool = True,
        smooth: bool = False
    ) -> Dict[str, str]:
        """
        Generate a line chart from DataFrame.

        Args:
            data: Pandas DataFrame with data
            x_column: Column name for X-axis
            y_column: Column name for Y-axis
            title: Chart title
            output_filename: Output filename (without extension)
            show_markers: Show markers on data points
            smooth: Use smooth line (spline)

        Returns:
            Dict with 'html_path' and 'png_path'
        """
        try:
            fig = px.line(
                data,
                x=x_column,
                y=y_column,
                title=title,
                template='plotly_white',
                markers=show_markers
            )

            # Customize line appearance
            fig.update_traces(
                line=dict(color='#3b82f6', width=3),
                marker=dict(size=8, color='#3b82f6') if show_markers else None
            )

            # Customize layout
            fig.update_layout(
                font=dict(size=14, family='Arial, sans-serif'),
                title_font_size=20,
                title_font_color='#1f2937',
                xaxis_title=x_column.replace('_', ' ').title(),
                yaxis_title=y_column.replace('_', ' ').title(),
                hovermode='x unified',
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=60, r=40, t=80, b=60),
                height=500
            )

            # Add grid
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e5e7eb')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e5e7eb')

            # Customize hover template
            fig.update_traces(
                hovertemplate='<b>%{x}</b><br>Amount: £%{y:,.2f}<extra></extra>'
            )

            # Save files
            html_path = self.output_dir / f"{output_filename}.html"
            png_path = self.output_dir / f"{output_filename}.png"

            fig.write_html(html_path)

            try:
                fig.write_image(png_path, width=1200, height=600, scale=2)
            except Exception as e:
                logger.warning("png_export_failed", error=str(e))
                png_path = None

            logger.info("line_chart_generated", title=title, html_path=str(html_path))

            return {
                'html_path': str(html_path),
                'png_path': str(png_path) if png_path else None,
                'title': title,
                'type': 'line'
            }

        except Exception as e:
            logger.error("line_chart_generation_failed", error=str(e), title=title)
            raise

    def pie_chart(
        self,
        data: pd.DataFrame,
        names_column: str,
        values_column: str,
        title: str,
        output_filename: str,
        hole: float = 0.3
    ) -> Dict[str, str]:
        """
        Generate a pie chart (or donut chart) from DataFrame.

        Args:
            data: Pandas DataFrame with data
            names_column: Column name for category names
            values_column: Column name for values
            title: Chart title
            output_filename: Output filename (without extension)
            hole: Size of center hole (0=pie, 0.3=donut)

        Returns:
            Dict with 'html_path' and 'png_path'
        """
        try:
            fig = px.pie(
                data,
                names=names_column,
                values=values_column,
                title=title,
                template='plotly_white',
                hole=hole,
                color_discrete_sequence=self.color_schemes['recruitment']
            )

            # Customize layout
            fig.update_layout(
                font=dict(size=14, family='Arial, sans-serif'),
                title_font_size=20,
                title_font_color='#1f2937',
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05
                ),
                height=500
            )

            # Customize pie slices
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                textfont_size=12,
                marker=dict(line=dict(color='white', width=2)),
                hovertemplate='<b>%{label}</b><br>Amount: £%{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
            )

            # Save files
            html_path = self.output_dir / f"{output_filename}.html"
            png_path = self.output_dir / f"{output_filename}.png"

            fig.write_html(html_path)

            try:
                fig.write_image(png_path, width=1000, height=600, scale=2)
            except Exception as e:
                logger.warning("png_export_failed", error=str(e))
                png_path = None

            logger.info("pie_chart_generated", title=title, html_path=str(html_path))

            return {
                'html_path': str(html_path),
                'png_path': str(png_path) if png_path else None,
                'title': title,
                'type': 'pie'
            }

        except Exception as e:
            logger.error("pie_chart_generation_failed", error=str(e), title=title)
            raise

    def multi_line_chart(
        self,
        data: pd.DataFrame,
        x_column: str,
        y_columns: List[str],
        title: str,
        output_filename: str,
        legend_labels: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Generate a multi-line chart for comparing multiple series.

        Args:
            data: Pandas DataFrame with data
            x_column: Column name for X-axis
            y_columns: List of column names for Y-axis (multiple lines)
            title: Chart title
            output_filename: Output filename (without extension)
            legend_labels: Custom labels for legend (optional)

        Returns:
            Dict with 'html_path' and 'png_path'
        """
        try:
            fig = go.Figure()

            colors = self.color_schemes['recruitment']

            for i, y_col in enumerate(y_columns):
                label = legend_labels[i] if legend_labels and i < len(legend_labels) else y_col

                fig.add_trace(go.Scatter(
                    x=data[x_column],
                    y=data[y_col],
                    mode='lines+markers',
                    name=label,
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=6)
                ))

            # Customize layout
            fig.update_layout(
                title=title,
                font=dict(size=14, family='Arial, sans-serif'),
                title_font_size=20,
                title_font_color='#1f2937',
                xaxis_title=x_column.replace('_', ' ').title(),
                yaxis_title='Amount (£)',
                hovermode='x unified',
                template='plotly_white',
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=60, r=40, t=80, b=60),
                height=500,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            # Add grid
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e5e7eb')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e5e7eb')

            # Save files
            html_path = self.output_dir / f"{output_filename}.html"
            png_path = self.output_dir / f"{output_filename}.png"

            fig.write_html(html_path)

            try:
                fig.write_image(png_path, width=1200, height=600, scale=2)
            except Exception as e:
                logger.warning("png_export_failed", error=str(e))
                png_path = None

            logger.info("multi_line_chart_generated", title=title, html_path=str(html_path))

            return {
                'html_path': str(html_path),
                'png_path': str(png_path) if png_path else None,
                'title': title,
                'type': 'multi_line'
            }

        except Exception as e:
            logger.error("multi_line_chart_generation_failed", error=str(e), title=title)
            raise
