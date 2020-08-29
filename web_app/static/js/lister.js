var selected = [];

$(document).ready( function () {
    // -- Format Datatable
    
    $("#deleteConfirm").click(function(e){
        $("input[name='id']").val(selected.join("|"))
        
    });
    $('#dataTable').DataTable({
        select: {
            style: "multi"
        },
        "order": [[ 1, "desc" ]],
        'columnDefs': [{
            'targets': 0,
            'searchable': false,
            'orderable': false,
            "responsive": true,
            'render': function (data, type, full, meta) {
                return '<input type="checkbox" />';
            }
        }],
    });
    $("#dataTable tbody").on("click", "tr", function () {
        var id = this.dataset.id;
        var index = $.inArray(id, selected);

        if ( index === -1 ) {
            selected.push( id );
        } else {
            selected.splice( index, 1 );
        }
        $(this).find("input").prop("checked",index === -1)

        if (selected.length ==0){
            $("#del-btn").addClass("disabled");
        }else{
            $("#del-btn").removeClass("disabled");
        }

        if (selected.length ==1){
            $("#edit-btn").removeClass("disabled");
        }else{
            $("#edit-btn").addClass("disabled");
        }
    } );
});