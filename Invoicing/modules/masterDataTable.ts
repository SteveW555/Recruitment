export interface ProjectHours {
    employeeName: string;
    projects: [string, string, number][]; // [PayID, ProjectName, Hours, ]
}

export interface MasterDataEntry {
    employeeName: string;
    totalHours: number;
    hourlyRate: number;
    holidayHours: number;
    bonus: number;
    projectHours: ProjectHours;
}
