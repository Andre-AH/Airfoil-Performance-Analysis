# Import necessary libraries
from aeropy.xfoil_module import find_coefficients
import pandas as pd
from tabulate import tabulate
import seaborn as sns  
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import tkinter as tk  
from tkinter import ttk 

# Analysis configuration
AIRFOIL_LIST = ['naca0012', 'naca2412', 'naca4412', 'naca0015', 'naca23012']
REYNOLDS = 1e6
ALPHA_RANGE = range(-10, 25, 2)

def fetch_aerodynamic_coefficients(airfoil, alpha):
    """Fetch aerodynamic coefficients using XFOIL for given airfoil and angle of attack."""
    try:
        results = find_coefficients(airfoil=airfoil, alpha=alpha, Reynolds=REYNOLDS, iteration=50)
        return {
            'C_L': round(results['CL'], 3),
            'C_D': round(results['CD'], 3),
            'C_M': round(results['CM'], 3),
            'C_L/C_D': round(results['CL'] / results['CD'], 3) if results['CD'] != 0 else None
    }
    except Exception as e:
        print(f"Error processing {airfoil} at AoA {alpha}: {e}")
        return None

def analyze_airfoils():
    """Analyze all airfoils and return performance data."""
    performance_data = []
    for airfoil in AIRFOIL_LIST:
        for alpha in ALPHA_RANGE:  
            coefficients = fetch_aerodynamic_coefficients(airfoil, alpha)
            if coefficients:
                performance_data.append({'Airfoil': airfoil, 'Angle of Attack (deg)': alpha, **coefficients})
    return pd.DataFrame(performance_data)

def get_best_airfoils(df):
    """Get the best airfoil for each angle of attack."""
    best_airfoils = []
    
    for alpha in df['Angle of Attack (deg)'].unique():
        subset = df[df['Angle of Attack (deg)'] == alpha]
        
        best_cl = subset.loc[subset['C_L'].idxmax()]
        best_cd = subset.loc[subset['C_D'].idxmin()]
        best_lift_drag_ratio = subset.loc[subset['C_L/C_D'].idxmax()]
        
        best_airfoils.append({
            'Angle of Attack (deg)': alpha,
            'Best C_L Airfoil': best_cl['Airfoil'],
            'Best C_L': best_cl['C_L'],
            'Best C_D Airfoil': best_cd['Airfoil'],
            'Best C_D': best_cd['C_D'],
            'Best L/D Airfoil': best_lift_drag_ratio['Airfoil'],
            'Best L/D Ratio': best_lift_drag_ratio['C_L/C_D']
        })
    
    return pd.DataFrame(best_airfoils)

def create_gui(best_airfoils):
    """Create a GUI window to display the best airfoils."""
    root = tk.Tk()
    root.title("Best Airfoil Analysis")

    tree = ttk.Treeview(root, columns=list(best_airfoils.columns), show='headings')
    tree.pack(side='top', fill='both', expand=True)

    # Set headings and center them
    for column in best_airfoils.columns:
        tree.heading(column, text=column, anchor='center')
        tree.column(column, anchor='center', width=100)

    # Insert rows into the treeview
    for index, row in best_airfoils.iterrows():
        tree.insert("", "end", values=list(row))

    scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side='right', fill='y')

    root.geometry("1600x500")
    root.mainloop()

def export_results(df, best_airfoils):
    """Export results to CSV and PDF."""

    # Export to CSV
    df.to_csv('airfoil_performance_table.csv', index=False)

    # Export to PDF
    with PdfPages('airfoil_performance_table.pdf') as pdf:
        # Add a title page with details
        plt.figure(figsize=(14, 10))
        plt.text(0.5, 0.5, 'Airfoil Performance Analysis\n\n'
                           f'Reynolds Number: {REYNOLDS:.1e}\n'
                           f'Airfoils Analyzed: {", ".join(AIRFOIL_LIST)}\n',
                 fontsize=18, ha='center', va='center')
        plt.axis('off')  
        pdf.savefig() 
        plt.close()

        plt.figure(figsize=(14, 10))
        sns.lineplot(data=df, x='Angle of Attack (deg)', y='C_L', hue='Airfoil', marker='o')
        plt.title('Lift Coefficient vs. Angle of Attack')
        plt.xlabel('Angle of Attack (degrees)')
        plt.ylabel('Lift Coefficient')
        plt.legend()
        plt.grid()
        pdf.savefig()  
        plt.close()

        plt.figure(figsize=(14, 10))
        sns.lineplot(data=df, x='Angle of Attack (deg)', y='C_L/C_D', hue='Airfoil', marker='o')
        plt.title('Lift-to-Drag Ratio vs. Angle of Attack')
        plt.xlabel('Angle of Attack (degrees)')
        plt.ylabel('Lift-to-Drag Ratio')
        plt.legend()
        plt.grid()
        pdf.savefig()  
        plt.close()

        plt.figure(figsize=(14, 10))
        for airfoil in df['Airfoil'].unique():
            airfoil_data = df[df['Airfoil'] == airfoil]
            sns.lineplot(data=airfoil_data, x='C_D', y='C_L', label=airfoil, marker='o')

        plt.title('Lift Coefficient vs. Drag Coefficient')
        plt.xlabel('Drag Coefficient (C_D)')
        plt.ylabel('Lift Coefficient (C_L)')
        plt.legend()
        plt.grid()
        pdf.savefig() 
        plt.close()

        # Create a table for best airfoils
        plt.figure(figsize=(14, 10))
        plt.axis('tight')
        plt.axis('off')
        table_data = best_airfoils.values
        column_labels = best_airfoils.columns.tolist()
        plt.table(cellText=table_data, colLabels=column_labels, cellLoc='center', loc='center')
        plt.title('Best Airfoils for Each Angle of Attack', fontsize=18)
        pdf.savefig()  
        plt.close()

def main():
    df = analyze_airfoils()
    best_airfoils = get_best_airfoils(df)
    export_results(df, best_airfoils)
    create_gui(best_airfoils) 

if __name__ == "__main__":
    main()
